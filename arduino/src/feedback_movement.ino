#include <Wire.h>   // This is added here because the SDPArduino library doesn't compile otherwise (in Arduino IDE)
#include <SoftwareSerial.h>   // We need this even if we're not using a SoftwareSerial object
#include <SerialCommand.h>
#include <SDPArduino.h>
#include <string.h>

SerialCommand comm;   // We create a SerialCommand object

int LEFT_MOTOR = 1;
int RIGHT_MOTOR = 2;
int BACK_MOTOR = 3;
int KICK_MOTOR = 4;
float KICK_TIME = 0.25; // TEST for the time to open/close (at full power)
// Will use this time to accomodate grabbing (depending on the power)

void setup()
{
    pinMode(13,OUTPUT);      // initialize pin 13 as digital output (LED)
    pinMode(8, OUTPUT);      // initialize pin 8 to control the radio
    digitalWrite(8,HIGH);    // select the radio

    Serial.begin(9600); // start the serial port at 9600 baud

    // Setup callbacks for SerialCommand commands
    comm.addCommand("ON", LED_on);          // Turns LED on
    comm.addCommand("OFF", LED_off);        // Turns LED off

    comm.addCommand("MOVE", move_wrapper);
    comm.addCommand("ROTATE", rotate_wrapper);
    comm.addCommand("STOP", stop_all);
    comm.addCommand("ACTION", kg_motor);

    comm.setDefaultHandler(unrecognized);  // Handler for command that isn't matched  (says "Command not recognized.")

    SDPsetup();
    Serial.println("Ready");

}

void loop()
{
    if (Serial.available()) {
        comm.readSerial(); // We don't do much, just process serial commands
    }
}


// Parse the serial command and call the movement function
void move_wrapper(){
    char *type;
    int power;

    type = comm.next();

    if (strcmp (type, "STRAIGHT") == 0){

        power = atoi(comm.next());
        move_straight(power);
    }

    else if (strcmp (type, "SIDEWAYS") == 0){
        char *direction = comm.next();
        int dir_bool = 1;

        if (strcmp (direction, "L") == 0){
            dir_bool = -1;
        }
        power = atoi(comm.next());
        move_sideways(dir_bool, power);
    }

    else if (strcmp (type, "DIAGONAL") == 0){
        char *direction = comm.next();
        int dir_bool = 1;

        if (strcmp (direction, "L") == 0){
            dir_bool = -1;
        }
        power = atoi(comm.next());
        move_diagonal(dir_bool, power);
    }

}


// Individual motor move function
// If the printing will not be necessary anymore, this function can just be replaced
//// with motorMove() in all the specific functions below
void move_motor(int motor_num, int power) {

    motorMove(motor_num, power);
    Serial.print(motor_num);
    Serial.print(" motor moving at ");
    Serial.println(power);
}

// Move straight (Forwards / Backwards)
void move_straight(int power) {
    move_motor(LEFT_MOTOR, power);
    move_motor(RIGHT_MOTOR, power);
}

// Move sideways (Left / Right)
void move_sideways(int dir_bool, int power) {
    move_motor(BACK_MOTOR, dir_bool * power);
    // dir_bool = -1 OR 1 for Left / Right
    // See how you can compensate the rotation with the front wheels
}

// Diagonal movement (Left / Right)
void move_diagonal(int dir_bool, int power){
    if(dir_bool == -1){ //LEFT
        move_motor(BACK_MOTOR, power);
        move_motor(LEFT_MOTOR, -power);
    }
    else {
        move_motor(BACK_MOTOR, power);
        move_motor(RIGHT_MOTOR, power);
    }
}

// Stop all motors
void stop_all() {
    motorAllStop();
    Serial.println("All motors off");
}

// Parse the serial command and and call the rotate function
void rotate_wrapper(){
    char *direction;
    int power;
    float time_turn;

    direction = comm.next();
    Serial.println(direction);
    power = atoi(comm.next());
    time_turn = atof(comm.next());

    int dir_bool = -1;
    if (strcmp (direction, "L") == 0){
        dir_bool = 1;
    }

    rotate(dir_bool, power, time_turn);
}


// Rotate function
void rotate(int dir_bool, int power, float time_turn) {

    move_motor(LEFT_MOTOR, dir_bool * -1 * power);
    move_motor(RIGHT_MOTOR, dir_bool * power);
    move_motor(BACK_MOTOR, dir_bool * -0.8 * power);

    delay(time_turn*1000);
    motorAllStop();
}

// Kicker / Grabber wrapper function

void kg_motor() {
    char *action;
    int power;

    action = comm.next();
    power = atoi(comm.next());

    if (strcmp (action, "KICK") == 0){
        kick(power);
    }
    else if (strcmp(action, "GRAB") == 0){
        grab(power);
    }
}


// Kicker

void kick(int power) {

    if (power != 100){
        float time_move = (200-power)/100 * KICK_TIME;
        move_motor(KICK_MOTOR, power);
        delay(time_move*1000);
    }
    else{
        move_motor(KICK_MOTOR, power);
        delay(KICK_TIME*1000);
    }

    Serial.println("Kicking");

    motorAllStop();
}


// Grabber

void grab(int power) {
    if (power != 100){
        float time_move = (200-power)/100 * KICK_TIME;
        move_motor(KICK_MOTOR, -power);
        delay(time_move*1000);
    }
    else{
        move_motor(KICK_MOTOR, -power);
        delay(KICK_TIME*1000);
    }

    Serial.println("Grabbing");
    motorAllStop();
}



// LEDs
void LED_on()
{
    Serial.println("LED on");
    digitalWrite(13, HIGH);
}

void LED_off()
{
    Serial.println("LED off");
    digitalWrite(13, LOW);
}

// This gets set as the default handler, and gets called when no other command matches.
void unrecognized(const char *command)
{
    Serial.println("Command not recognized.");
}
