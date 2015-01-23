#include <SoftwareSerial.h>   // We need this even if we're not using a SoftwareSerial object
#include <SerialCommand.h>
#include <SDPArduino.h>
#include <string.h>

SerialCommand comm;   // We create a SerialCommand object

void setup()
{
  pinMode(13,OUTPUT);      // initialize pin 13 as digital output (LED)
  pinMode(8, OUTPUT);      // initialize pin 8 to control the radio
  digitalWrite(8,HIGH);    // select the radio

  Serial.begin(9600); // start the serial port at 9600 baud

  // Setup callbacks for SerialCommand commands
  comm.addCommand("ON", LED_on);          // Turns LED on
  comm.addCommand("OFF", LED_off);        // Turns LED off
  comm.addCommand("HELLO", SayHello);     // Echos the string argument back
  comm.addCommand("BLINK", blink_n_times);  //  Blinks LED a specified number of times
  comm.addCommand("ADD", AddNumbers);    // Adds two integers together

  comm.addCommand("LEFT_MOTOR", left_motor);
  comm.addCommand("RIGHT_MOTOR", right_motor);
  comm.addCommand("BACK_MOTOR", back_motor);
  comm.addCommand("KICK_MOTOR", kick_motor);

  comm.setDefaultHandler(unrecognized);  // Handler for command that isn't matched  (says "Command not recognized.")

  SDPsetup();
  Serial.println("Ready");

}

void loop()
{
  if (Serial.available()) {
    //Serial.print(1);
    comm.readSerial(); // We don't do much, just process serial commands
  }
}

void left_motor() {

  char *state;
  char *direction;
  int power;

  state = comm.next();
  direction = comm.next();
  power = atoi(comm.next());

  Serial.print("left_motor function is on");

	if (strcmp(state, "ON")==0) {
		if (strcmp(direction, "BACKWARDS")==0) {
      Serial.print("Motor is moving backwards");
			motorBackward(1, power);
		}
    else if (strcmp(direction, "FORWARDS")==0) {
      Serial.print("Motor is moving forwards");
			motorForward(1, power);
		}
	} else if (strcmp(state, "OFF")==0) {
		motorStop(1);
	}

}

void right_motor() {

  char *state;
  char *direction;
  int power;

  state = comm.next();
  direction = comm.next();
  power = atoi(comm.next());

  if (strcmp(state, "ON")) {
    if (strcmp(direction, "BACKWARDS")) {
      Serial.print("Motor is moving backwards");
			motorBackward(2, power);
		}
    else if (strcmp(direction, "FORWARDS")) {
      Serial.print("Motor is moving forwards");
			motorForward(2, power);
		}
  } else if (strcmp(state, "OFF")) {
		motorStop(2);
	}
}

void back_motor() {

  char *state;
  char *direction;
  int power;

  state = comm.next();
  direction = comm.next();
  power = atoi(comm.next());

  if (strcmp(state, "ON")) {
    if (strcmp(direction, "BACKWARDS")) {
      Serial.print("Motor is moving backwards");
			motorBackward(3, power);
		}
    else if (strcmp(direction, "FORWARDS")) {
      Serial.print("Motor is moving forwards");
			motorForward(3, power);
		}
  } else if (strcmp(state, "OFF")) {
		motorStop(3);
	}
}

void kick_motor() {

  char *state;
  char *direction;
  int power;

  state = comm.next();
  direction = comm.next();
  power = atoi(comm.next());

  if (strcmp(state, "ON")) {
    if (strcmp(direction, "BACKWARDS")) {
      Serial.print("Motor is moving backwards");
      motorBackward(4, power);
    }
    else if (strcmp(direction, "FORWARDS")) {
      Serial.print("Motor is moving forwards");
      motorForward(4, power);
    }
  } else if (strcmp(state, "OFF")) {
    motorStop(4);
  }
}

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

void SayHello()
{
  char *arg;
  arg = comm.next();    // Get the next argument from the SerialCommand object buffer
  if (arg != NULL)
  {
    Serial.print("Hello ");
    Serial.println(arg);
  }
  else {
    Serial.println("Hello there!");
  }
}

void blink_n_times()
{
  int aNumber;
  char *arg;

  Serial.println("Processing command...");
  arg = comm.next();
  if (arg != NULL)
  {
    aNumber = atoi(arg);    // Converts a char string to an integer
    Serial.print("First argument was: ");
    Serial.println(aNumber);
  }

  int i = 0;
  for (i; i<aNumber; i++)
  {
    delay(500);
    LED_on();
    delay(500);
    LED_off();
  }

}

void AddNumbers()
{
  char *arg1;
  char *arg2;
  int firstNumber;
  int secondNumber;
  int sum;

  arg1 = comm.next();
  arg2 = comm.next();
  if (arg1 != NULL && arg2 != NULL)
  {
    firstNumber=atoi(arg1);
    secondNumber=atoi(arg2);
    sum = firstNumber + secondNumber;

    Serial.print(firstNumber);
    Serial.print(" + ");
    Serial.print(secondNumber);
    Serial.print(" = ");
    Serial.println(sum);
  }
  else
  {
    Serial.println("Please enter two arguments.");
  }
}

// This gets set as the default handler, and gets called when no other command matches.
void unrecognized(const char *command)
{
  Serial.println("Command not recognized.");
}