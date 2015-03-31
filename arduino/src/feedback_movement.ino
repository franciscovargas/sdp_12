#include <Wire.h>   // This is added here because the SDPArduino library doesn't compile otherwise (in Arduino IDE)
#include <SoftwareSerial.h>   // We need this even if we're not using a SoftwareSerial object
#include <SerialCommand.h>
#include <SDPArduino.h>
#include <string.h>

# define EVENT_BUFFER_SIZE 60

SerialCommand comm;

boolean kicker_running = false;
boolean stopping = false;

int LEFT_MOTOR = 1;
int RIGHT_MOTOR = 2;
int BACK_MOTOR = 3;
int KICK_MOTOR = 4;
int GRAB_MOTOR = 0;
float KICK_TIME = 0.4;
float GRAB_TIME = 0.4;
// Will use this time to accommodate grabbing (depending on the power)

// Stores commands to be executed.
namespace event_loop {
  struct command_entry {
    int motor;
    int speed;
    unsigned long start_time;
    bool todo;
  };
  
  struct command_entry event_buffer[EVENT_BUFFER_SIZE];
  
  void add_command_head(int motor, int speed, unsigned long start_time) {
   // Loop through the array and put this command in the first non-todo
   int i;
   int empty_slot = -1;
   for (i = 0; i < EVENT_BUFFER_SIZE; i++) {
     if (event_buffer[i].todo == false) {
       empty_slot = i;
       break;
     }
   }
   
   // If there is no empty slot, drop the command and print error to serial
   if (empty_slot == -1) {
     Serial.println("error: command buffer full, command dropped");
     return;
   }
      
   event_buffer[empty_slot].motor = motor;
   event_buffer[empty_slot].speed = speed;
   event_buffer[empty_slot].start_time = start_time;
   event_buffer[empty_slot].todo = true;
  }
  
  // Sets the value of "todo" to false in each buffer entry
  void initialise_buffer() {
    int i;
    for (i = 0; i < EVENT_BUFFER_SIZE; i++)
    {
      event_buffer[i].todo = false;
    }
  }
  
  void process_list() {
    int i;
    for (i = 0; i < EVENT_BUFFER_SIZE; i++) {
      if (event_buffer[i].todo && event_buffer[i].start_time <= millis()) {
        motorMove(event_buffer[i].motor, event_buffer[i].speed);
  
        // Set todo to false so this buffer slot can be reused.
        event_buffer[i].todo = false;
      }
    }
  }
}

void setup() {
    pinMode(13,OUTPUT);      // initialize pin 13 as digital output (LED)
    pinMode(8, OUTPUT);      // initialize pin 8 to control the radio
    digitalWrite(8,HIGH);    // select the radio

    Serial.begin(9600); // start the serial port at 9600 baud
    
    event_loop::initialise_buffer();

    // Setup callbacks for SerialCommand commands
    comm.addCommand("A", stop_all);
    comm.addCommand("B", move_straight);
    comm.addCommand("C", stop_straight);
    comm.addCommand("D", move_sideways);
    comm.addCommand("E", move_diagonal);
    comm.addCommand("F", rotate);
    comm.addCommand("G", rotate_and_grab);
    comm.addCommand("H", stop_rotating);
    comm.addCommand("I", grab);
    comm.addCommand("J", grab_continuous);
    comm.addCommand("K", kick);
    comm.addCommand("S", speed_kick);

    comm.setDefaultHandler(unrecognized);  // Handler for command that isn't matched  (says "Command not recognized.")

    SDPsetup();
    Serial.println("Ready");
}

void loop() {
    if (Serial.available()) {
        comm.readSerial(); // We don't do much, just process serial commands
    }
    
    event_loop::process_list();
    
    // Empyt the buffer if stop_all() was called.
    if (stopping == true) {
        event_loop::initialise_buffer();
        
        stopping = false;
    }
}

// Individual motor move function
// If the printing will not be necessary anymore, this function can just be replaced
// with motorMove() in all the specific functions below
void move_motor(int motor_num, int power) {

    motorMove(motor_num, power);
    Serial.print(motor_num);
    Serial.print(" motor moving at ");
    Serial.println(power);
}

// Move straight (Forwards / Backwards)
void move_straight() {
    int power;
    power = atoi(comm.next());

    event_loop::add_command_head(LEFT_MOTOR, power, millis());
    event_loop::add_command_head(RIGHT_MOTOR, power, millis());
}

void stop_straight() {
    int power;
    power = atoi(comm.next());
    
    event_loop::add_command_head(LEFT_MOTOR, power, millis());
    event_loop::add_command_head(RIGHT_MOTOR, power, millis());
    
    event_loop::add_command_head(LEFT_MOTOR, 0, millis()+400);
    event_loop::add_command_head(RIGHT_MOTOR, 0, millis()+400);
}

// Move sideways (Left / Right)
void move_sideways() {
    int power;
    power = atoi(comm.next());

    event_loop::add_command_head(BACK_MOTOR, power, millis());
}

// Diagonal movement (Left / Right)
void move_diagonal() {
    int power;
    power = atoi(comm.next());

    if(power < 0) { //LEFT
        event_loop::add_command_head(LEFT_MOTOR, -power, millis());
        event_loop::add_command_head(BACK_MOTOR, power, millis());
    }
    else {
        event_loop::add_command_head(RIGHT_MOTOR, power, millis());
        event_loop::add_command_head(BACK_MOTOR, power, millis());
    }
}

// Stop all motors
void stop_all() {
    event_loop::add_command_head(KICK_MOTOR, 0, millis());
    event_loop::add_command_head(GRAB_MOTOR, 0, millis());
    event_loop::add_command_head(LEFT_MOTOR, 0, millis());
    event_loop::add_command_head(RIGHT_MOTOR, 0, millis());
    event_loop::add_command_head(BACK_MOTOR, 0, millis());
    
    stopping = true;
    Serial.println("All motors off");
}

// Rotate functions
void rotate() {
    int power;
    power = atoi(comm.next());
    
    event_loop::add_command_head(LEFT_MOTOR, -power, millis());
    event_loop::add_command_head(RIGHT_MOTOR, power, millis());
    event_loop::add_command_head(BACK_MOTOR, -0.8 * power, millis());
}

void rotate_and_grab() {
    int power_rotate;
    int power_grab;
    power_rotate = atoi(comm.next());
    power_grab = atoi(comm.next());
    
    //Rotate
    event_loop::add_command_head(LEFT_MOTOR, -power_rotate, millis());
    event_loop::add_command_head(RIGHT_MOTOR, power_rotate, millis());
    event_loop::add_command_head(BACK_MOTOR, -0.8 * power_rotate, millis());
    // Grab
    event_loop::add_command_head(GRAB_MOTOR, -power_grab, millis());
}

void stop_rotating() {
    int power;

    power = atoi(comm.next());

    event_loop::add_command_head(LEFT_MOTOR, -power, millis());
    event_loop::add_command_head(RIGHT_MOTOR, power, millis());
    event_loop::add_command_head(BACK_MOTOR, -0.8 * power, millis());
    
    event_loop::add_command_head(LEFT_MOTOR, 0, millis()+400);
    event_loop::add_command_head(RIGHT_MOTOR, 0, millis()+400);
    event_loop::add_command_head(BACK_MOTOR, 0, millis()+400);
    event_loop::add_command_head(GRAB_MOTOR, 0, millis()+400);
}

// Kicker
void kick() {
    int power;
    power = atoi(comm.next());
    
    // Move back and open grabber
    event_loop::add_command_head(KICK_MOTOR, 40, millis());
    event_loop::add_command_head(GRAB_MOTOR, -50, millis());

    // Kick
    event_loop::add_command_head(KICK_MOTOR, -power, millis()+200);
    
    // Stop both motors.
    event_loop::add_command_head(GRAB_MOTOR, 0, millis()+200);
    event_loop::add_command_head(KICK_MOTOR, 0, millis()+200+(KICK_TIME*1000));

    Serial.println("Kicking");
}

// Evade and kick
void speed_kick() {
    int kick_power = atoi(comm.next());
    int moveside_power = atoi(comm.next());
    int moveback_power = atoi(comm.next());

    // Evade
    event_loop::add_command_head(GRAB_MOTOR, 30, millis());
    event_loop::add_command_head(BACK_MOTOR, moveside_power, millis());
    if(moveside_power > 0) {
        event_loop::add_command_head(LEFT_MOTOR, moveback_power, millis());
        event_loop::add_command_head(RIGHT_MOTOR, -moveback_power, millis());
    }
    else {
        event_loop::add_command_head(LEFT_MOTOR, -moveback_power, millis());
        event_loop::add_command_head(RIGHT_MOTOR, moveback_power, millis());
    }
    
    // stop all motors
    event_loop::add_command_head(BACK_MOTOR, 0, millis()+900);
    event_loop::add_command_head(LEFT_MOTOR, 0, millis()+900);
    event_loop::add_command_head(RIGHT_MOTOR, 0, millis()+900);
    event_loop::add_command_head(GRAB_MOTOR, 0, millis()+1000);

    // Move back and open grabber
    event_loop::add_command_head(KICK_MOTOR, 40, millis()+1100);
    event_loop::add_command_head(GRAB_MOTOR, -50, millis()+1100);

    // Kick
    event_loop::add_command_head(GRAB_MOTOR, 0, millis()+1250);
    event_loop::add_command_head(KICK_MOTOR, -kick_power, millis()+1250);
    
    // Stop kicker
    event_loop::add_command_head(KICK_MOTOR, 0, millis()+1250+(KICK_TIME*1000));

    Serial.println("Kicking");
}

// Move grabber.
void grabber_move(int power) {
    
    if (power != 100) {
        float time_move = (200-power)/100 * GRAB_TIME;
        
        // open the grabber and stop opening after (time_move*1000) miliseconds.
        event_loop::add_command_head(GRAB_MOTOR, power, millis());
        event_loop::add_command_head(GRAB_MOTOR, 0, millis()+(time_move*1000));
    }
    else {   
        // open the grabber and stop opening after (time_move*1000) miliseconds.
        event_loop::add_command_head(GRAB_MOTOR, -power, millis());
        event_loop::add_command_head(GRAB_MOTOR, 0, millis()+(GRAB_TIME*1000));
    }

    Serial.println("Grabbing");
}

// Decide whether to open or close the grabber
void grab() {
    int power;
    power = atoi(comm.next());
    
    if(power > 0) {
        // Open grabber.
        grabber_move(power);
    }
    else { 
        // Close grabber.
        grabber_move(power);
    }
}

void grab_continuous() {
    int power;
    power = atoi(comm.next());

    move_motor(GRAB_MOTOR, power);
    Serial.println("Graaaabing");
}

// This gets set as the default handler, and gets called when no other command matches.
void unrecognized(const char *command) {
    Serial.println("Command not recognized.");
}