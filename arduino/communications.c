#include <SoftwareSerial.h>   // We need this even if we're not using a SoftwareSerial object
#include <SerialCommand.h>

SerialCommand comm;   // We create a SerialCommand object

void setup()
{  
  pinMode(13,OUTPUT);      // initialize pin 13 as digital output (LED)
  pinMode(8, OUTPUT);      // initialize pin 8 to control the radio
  digitalWrite(8,HIGH);    // select the radio

  Serial.begin(9600); // start the serial port at 9600 baud

  // Setup callbacks for SerialCommand commands 
  comm.addCommand("ON",LED_on);          // Turns LED on
  comm.addCommand("OFF",LED_off);        // Turns LED off
  comm.addCommand("HELLO",SayHello);     // Echos the string argument back
  comm.addCommand("BLINK",blink_n_times);  //  Blinks LED a specified number of times
  comm.addCommand("ADD", AddNumbers);    // Adds two integers together
  comm.addDefaultHandler(unrecognized);  // Handler for command that isn't matched  (says "What?") 
  Serial.println("Ready"); 

}

void loop()
{  
  comm.readSerial();     // We don't do much, just process serial commands
}


void LED_on()
{
  Serial.println("LED on"); 
  digitalWrite(13,HIGH);  
}

void LED_off()
{
  Serial.println("LED off"); 
  digitalWrite(13,LOW);
}

void SayHello()
{
  char *arg;  
  arg = comm.next();    // Get the next argument from the SerialCommand object buffer
  if (arg != NULL)      // As long as it existed, take it
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
  Serial.println(arg);
  if (arg != NULL) 
  {
    aNumber=atoi(arg);    // Converts a char string to an integer
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
void unrecognized()
{
  Serial.println("Command not recognized."); 
}
