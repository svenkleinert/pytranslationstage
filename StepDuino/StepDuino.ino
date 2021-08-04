const byte DIRECTION_PIN = 3;
const byte STEP_PIN = 4;
const byte ENABLE_PIN = 10;
const byte SLEEP_PIN = 5;
const byte RESET_PIN = 6;


const byte MICROSTEPPING_PIN1 = 7;
const byte MICROSTEPPING_PIN2 = 8;
const byte MICROSTEPPING_PIN3 = 9;

const byte BOUNCER_PIN = 2;
const bool isBouncerOnHighSide = true;
bool wasHomingPerformed = false;

const byte MICROSTEPS_PER_STEP = 1;

const long baudrate = 115200;

const float screwPitch = 0.002;
const int stepsPerRevolution = 200;
const float stepsPerSecond = 1000.;

const float LOWER_BOUND = 0;
const float UPPER_BOUND = 0.298;

#include <FlexyStepper.h>
FlexyStepper stepper;

#include "Vrekrer_scpi_parser.h"
#define FIRMWARE_VERSION "1.0.0" // Firmware version
SCPI_Parser command_parser;

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(baudrate);
  
  pinMode(BOUNCER_PIN, INPUT_PULLUP);

  setupMicrostepping();
  
  pinMode(SLEEP_PIN, OUTPUT);
  digitalWrite(SLEEP_PIN, LOW);
  pinMode(RESET_PIN, OUTPUT);
  digitalWrite(RESET_PIN, HIGH);
  
  pinMode(ENABLE_PIN, OUTPUT);
  digitalWrite(ENABLE_PIN, LOW);
  

  stepper.connectToPins(STEP_PIN, DIRECTION_PIN);
  
  stepper.setSpeedInStepsPerSecond(stepsPerSecond);
  stepper.setAccelerationInStepsPerSecondPerSecond(100000.);

  command_parser.RegisterCommand("*IDN?", &scpiSendID);
  command_parser.RegisterCommand("*RST", &scpiReset);
  command_parser.RegisterCommand("*CLS", &scpiClearError);
  command_parser.RegisterCommand("*STB?", &scpiClearError);
  
  command_parser.SetCommandTreeBase("SYSTem");
  command_parser.RegisterCommand(":HOme", &scpiHomeSearch);
  command_parser.RegisterCommand(":STAte?", &scpiSendDeviceState);
  
  command_parser.SetCommandTreeBase("MOve");
  command_parser.RegisterCommand(":RELative", &scpiMoveRelative);
  command_parser.RegisterCommand(":RELative?", &scpiSendTimeMoveRelative);
  command_parser.RegisterCommand(":ABSolute", &scpiMoveAbsolute);
  command_parser.RegisterCommand(":ABSolute?", &scpiSendTimeMoveAbsolute);
  command_parser.RegisterCommand(":POSition", &scpiMoveAbsolute);
  command_parser.RegisterCommand(":POSition?", &scpiSendPosition);
  command_parser.RegisterCommand(":LIMits:MAXimum?", &scpiSendLimitsMax);
  command_parser.RegisterCommand(":LIMits:MINimum?", &scpiSendLimitsMin);
}  

void loop()
{
  // put your main code here, to run repeatedly:
  command_parser.ProcessInput(Serial, "\n");

  if(!stepper.motionComplete())
  {
    stepper.processMovement();
  }else{
    digitalWrite(SLEEP_PIN, LOW);
  }
  
}

void setupMicrostepping()
{
  pinMode(MICROSTEPPING_PIN1, OUTPUT);
  pinMode(MICROSTEPPING_PIN2, OUTPUT);
  pinMode(MICROSTEPPING_PIN3, OUTPUT);
  digitalWrite(MICROSTEPPING_PIN1, LOW);
  digitalWrite(MICROSTEPPING_PIN1, LOW);
  digitalWrite(MICROSTEPPING_PIN1, LOW);
  if(MICROSTEPS_PER_STEP == 2)
  {
    digitalWrite(MICROSTEPPING_PIN1, HIGH);
  }
  if(MICROSTEPS_PER_STEP == 4)
  {
    digitalWrite(MICROSTEPPING_PIN2, HIGH);
  }
  if(MICROSTEPS_PER_STEP == 8)
  {
    digitalWrite(MICROSTEPPING_PIN1, HIGH);
    digitalWrite(MICROSTEPPING_PIN2, HIGH);
  }
  if(MICROSTEPS_PER_STEP == 16)
  {
    digitalWrite(MICROSTEPPING_PIN3, HIGH);
  }
  if(MICROSTEPS_PER_STEP == 32)
  {
    digitalWrite(MICROSTEPPING_PIN1, HIGH);
    digitalWrite(MICROSTEPPING_PIN2, HIGH);
    digitalWrite(MICROSTEPPING_PIN3, HIGH);
  }
}

void homeSearch()
{
  digitalWrite(SLEEP_PIN, HIGH);
  stepper.moveToHomeInSteps(isBouncerOnHighSide?1:-1, stepsPerSecond, 1000000., BOUNCER_PIN);
  stepper.setTargetPositionInSteps(0);
  
  digitalWrite(SLEEP_PIN, LOW);
  wasHomingPerformed = true;
}

void moveAbsolute(float value)
{
  if(wasHomingPerformed and stepper.motionComplete() and value >= LOWER_BOUND and value <= UPPER_BOUND)
  {
    digitalWrite(SLEEP_PIN, HIGH);
    long pos = -positionToSteps(value);
    stepper.setTargetPositionInSteps(pos);
  }
}

void moveRelative(float value)
{
  if(wasHomingPerformed and stepper.motionComplete())
  {
    long steps = - positionToSteps(value);
    if(stepper.getCurrentPositionInSteps() + steps <= positionToSteps(LOWER_BOUND) and stepper.getCurrentPositionInSteps() + steps >= - positionToSteps(UPPER_BOUND))
    {
      digitalWrite(SLEEP_PIN, HIGH);
      stepper.setTargetPositionRelativeInSteps(steps);
      
    }
  }
}

//SCPI commands
void scpiSendID(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  char idn[] = "STEPDUINO,001,001,"FIRMWARE_VERSION;
  interface.println(idn);
}
void scpiReset(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{

}

void scpiClearError(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{

}

void scpiHomeSearch(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  homeSearch();
}

void scpiSendDeviceState(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  scpiReplyCommand(commands, interface);
  if(!wasHomingPerformed)
  {
    interface.println("UNINITIALIZED");
  }else{
    if(!stepper.motionComplete())
    {
      interface.println("MOVING");
    }else{
      interface.println("READY");
    }
  }
  
}

void scpiMoveRelative(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  if(parameters.Size()>0)
  {
    String s(parameters[0]);
    float pos = s.toFloat();
    moveRelative(pos);
  }
}

void scpiSendTimeMoveRelative(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  if(parameters.Size()>0)
  {
    String s(parameters[0]);
    float t = 1.1 * positionToSteps(s.toFloat()) / stepsPerSecond;
    scpiReplyCommand(commands, interface);
    interface.println(t, 6);
  }
}

void scpiMoveAbsolute(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  if(parameters.Size()>0)
  {
    String s(parameters[0]);
    float pos = s.toFloat();
    moveAbsolute(pos);
  }
}

void scpiSendTimeMoveAbsolute(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  if(parameters.Size()>0)
  {
    String s(parameters[0]);
    float t = 1.1 * (float)abs(-stepper.getCurrentPositionInSteps() - positionToSteps(s.toFloat())) / stepsPerSecond;
    scpiReplyCommand(commands, interface);
    interface.println(t, 6);
  }
}

void scpiSendPosition(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  if( parameters.Size() == 0)
  {
    scpiReplyCommand(commands, interface);
    if(stepper.getCurrentPositionInSteps() == -1)
    { 
      interface.println("NONE");
    }else{
      float pos = - stepsToPosition(stepper.getCurrentPositionInSteps()); 
      interface.println(pos, 6);
    }
  }else{
    scpiSendTimeMoveAbsolute(commands, parameters, interface);
  }
}

void scpiSendLimitsMin(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  scpiReplyCommand(commands, interface);
  interface.println(LOWER_BOUND, 6);
}

void scpiSendLimitsMax(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  scpiReplyCommand(commands, interface);
  interface.println(UPPER_BOUND, 6);
}

void scpiReplyCommand(SCPI_Commands commands, Stream &interface)
{
  for(int i=0; i<commands.Size()-1; i++)
    {
      interface.print(commands[i]);
      interface.print(":");
    }
    interface.print(commands.Last());
}

float stepsToPosition(long steps)
{
 return steps * ((float)screwPitch / stepsPerRevolution / MICROSTEPS_PER_STEP);
}

long positionToSteps(float pos)
{
  return pos / screwPitch * stepsPerRevolution * MICROSTEPS_PER_STEP;
}
