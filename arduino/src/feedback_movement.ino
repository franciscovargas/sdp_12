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
float KICK_TIME = 0.75; // TEST for the time to open/close (at full power)
// Will use this time to accomodate grabbing (depending on the power)
float GRAB_TIME = 0.5;

void setup() {
    pinMode(13,OUTPUT);      // initialize pin 13 as digital output (LED)
    pinMode(8, OUTPUT);      // initialize pin 8 to control the radio
    digitalWrite(8,HIGH);    // select the radio

    Serial.begin(9600); // start the serial port at 9600 baud

    // Setup callbacks for SerialCommand commands
    comm.addCommand("ON", LED_on);          // Turns LED on
    comm.addCommand("OFF", LED_off);        // Turns LED off

    comm.addCommand("MOVE", move_wrapper);
    comm.addCommand("STOP_STRAIGHT", stop_straight_wrapper);
    comm.addCommand("ROTATE", rotate_wrapper);
    comm.addCommand("STOP_ROTATE", stop_rotating_wrapper);
    comm.addCommand("STOP", stop_all);
    comm.addCommand("ACTION", kg_wrapper);
    comm.addCommand("RG", rg_wrapper);

    comm.setDefaultHandler(unrecognized);  // Handler for command that isn't matched  (says "Command not recognized.")

    SDPsetup();
    Serial.println("Ready");

}

void loop() {
    if (Serial.available()) {
        comm.readSerial(); // We don't do much, just process serial commands
    }
}


// Parse the serial command and call the movement function
// Direction depends on if POWER is positive or negative
// Syntax: MOVE TYPE POWER
void move_wrapper() {
    char *type;
    int power;

    type = comm.next();
    power = atoi(comm.next());

    if (strcmp(type, "STRAIGHT") == 0) {
        move_straight(power);
    }
    else if (strcmp(type, "SIDEWAYS") == 0) {
        move_sideways(power);
    }
    else if (strcmp(type, "DIAGONAL") == 0) {
        move_diagonal(power);
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
void move_straight(int power) {
    move_motor(LEFT_MOTOR, power);
    move_motor(RIGHT_MOTOR, power);
}

// Move sideways (Left / Right)
void move_sideways(int power) {
    move_motor(BACK_MOTOR, power);
    // See how you can compensate the rotation with the front wheels
}

// Diagonal movement (Left / Right)
void move_diagonal(int power) {
    if(power < 0) { //LEFT
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
// Syntax: ROTATE POWER
void rotate_wrapper() {
    int power;

    power = atoi(comm.next());

    rotate(power);
}


// Rotate function
void rotate(int power) {

    move_motor(LEFT_MOTOR, -1 * power);
    move_motor(RIGHT_MOTOR, power);
    move_motor(BACK_MOTOR, -0.8 * power);
}

// Rotate and grab function
void rg_wrapper() {
    int power_rotate;
    int power_grab;

    power_rotate = atoi(comm.next());
    power_grab = atoi(comm.next());

    rotate_and_grab(power_rotate, power_grab);
}

void rotate_and_grab(int power_rotate, int power_grab){
    //Rotate
    move_motor(LEFT_MOTOR, -1 * power_rotate);
    move_motor(RIGHT_MOTOR, power_rotate);
    move_motor(BACK_MOTOR, -0.8 * power_rotate);
    // Grab
    move_motor(KICK_MOTOR, -power_grab);
}

void stop_rotating_wrapper() {
    int power;

    power = atoi(comm.next());

    stop_rotating(power);
}

void stop_rotating(int power) {

    move_motor(LEFT_MOTOR, -1 * power);
    move_motor(RIGHT_MOTOR, power);
    move_motor(BACK_MOTOR, -0.8 * power);
    delay(500);
    stop_all();
}

void stop_straight_wrapper() {
    int power;

    power = atoi(comm.next());

    stop_rotating(power);
}

void stop_straight(int power) {
    move_motor(LEFT_MOTOR, power);
    move_motor(RIGHT_MOTOR, power);
    delay(500);
    stop_all();
}

// Kicker / Grabber wrapper function
// Syntax: ACTION TYPE POWER
void kg_wrapper() {
    char *type;
    int power;

    type = comm.next();
    power = atoi(comm.next());

    if (strcmp(type, "KICK") == 0) {
        kick(power);
    }
    else if (strcmp(type, "GRAB") == 0) {
        grab(power);
    }
    else if (strcmp(type, "GRAB_CONT") == 0) {
        grab_continuous(power);
    }
}


// Kicker
void kick(int power) {

    if (power != 100) {
        float time_move = (200-power)/100 * KICK_TIME;
        move_motor(KICK_MOTOR, power);
        delay(time_move*1000);
    }
    else {
        move_motor(KICK_MOTOR, power);
        delay(KICK_TIME*1000);
    }

    Serial.println("Kicking");

    motorAllStop();
}


// Grabber
void grab(int power) {
    if (power != 100) {
        float time_move = (200-power)/100 * GRAB_TIME;
        move_motor(KICK_MOTOR, -power);
        delay(time_move*1000);
    }
    else {
        move_motor(KICK_MOTOR, -power);
        delay(GRAB_TIME*1000);
    }

    Serial.println("Grabbing");
    motorAllStop();
}

void grab_continuous(int power) {
    move_motor(KICK_MOTOR, -power);
    Serial.println("Graaaabing");
}


// LEDs
void LED_on() {
    Serial.println("LED on");
    digitalWrite(13, HIGH);
}

void LED_off() {
    Serial.println("LED off");
    digitalWrite(13, LOW);
}

// This gets set as the default handler, and gets called when no other command matches.
void unrecognized(const char *command) {
    Serial.println("Command not recognized.");
}
