#include <SoftwareSerial.h>   // We need this even if we're not using a SoftwareSerial object
#include <SerialCommand.h>
#include <SDPArduino.h>
#include <string.h>

SerialCommand comm;   // We create a SerialCommand object

#define LEFT_MOTOR = 1;
#define RIGHT_MOTOR = 2;
#define BACK_MOTOR = 3;
#define KICK_MOTOR = 4;

void setup()
{
  pinMode(13,OUTPUT);      // initialize pin 13 as digital output (LED)
  pinMode(8, OUTPUT);      // initialize pin 8 to control the radio
  digitalWrite(8,HIGH);    // select the radio

  Serial.begin(9600); // start the serial port at 9600 baud

  // Setup callbacks for SerialCommand commands
  comm.addCommand("ON", LED_on);          // Turns LED on
  comm.addCommand("OFF", LED_off);        // Turns LED off

  comm.addCommand("ROTATE", rotate_wrapper);
  comm.addCommand("RIGHT_MOTOR", right_motor_wrapper);
  comm.addCommand("BACK_MOTOR", back_motor_wrapper);
  comm.addCommand("KICK_MOTOR", kick_motor_wrapper);
  comm.addCommand("ROTATE_LEFT", rotate_left);
  comm.addCommand("STOP_ALL", stop_all);

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


// Parse the serial command and and call the rotate function
void rotate_wrapper(){
    char *direction;
    int power;
    float time_turn;

    direction = comm.next();
    power = atoi(comm.next());
    time_turn = atof(comm.next());

    if (direction == "L"){
        dir_bool = -1;
    }
    else {
        dir_bool = 1;
    }

    rotate(dir_bool, power, time_turn);
}


// Rotate function
void rotate(dir_bool, power, time_turn) {

    move_motor(LEFT_MOTOR, dir_bool * -1 * power, time_turn);
    move_motor(RIGHT_MOTOR, dir_bool * power, time_turn);
    move_motor(BACK_MOTOR, dir_bool * -0.8 * power, time_turn);

    motorAllStop();
}

// Individual motor move function
void move_motor(int motor_num, int power, float time_move) {

    motorMove(motor_num, power);
    Serial.print("%d motor moving at %d \n.", motor_num, power);

    delay(time_move);
    motorAllStop();
}

// Move straight (Forwards / Backwards)
void move_straight(int power, float time_move) {
    motorMove(LEFT_MOTOR, power);
    motorMove(RIGHT_MOTOR, power);

    delay(time_move);
    motorAllStop();
}

// Move sideways (Left / Right)
void move_sideways(int dir_bool, int power, float time_move) {
    motorMove(BACK_MOTOR, dir_bool * power);
    // dir_bool = -1 OR 1 for Left / Right
    // See how you can compensate the rotation with the front wheels

    delay(time_move);
    motorAllStop();
}

// Diagonal movement (Left / Right)
void move_diagonal(int dir_bool, int power, float time_move){
    if(dir_bool == 1){ //LEFT
        motorMove(BACK_MOTOR, power);
        motorMove(LEFT_MOTOR, power);
    }
    else {
        motorMove(BACK_MOTOR, power);
        motorMove(RIGHT_MOTOR, power);
    }
}
