const byte dirPin = 3;
const byte stepPin = 4;
const byte enablePin = 10;

const byte bouncerPin = 2;
const bool isBouncerOnHighSide = true;

const int baudrate = 115200;

const float screwPitch = 0.002;
const int stepsPerRevolution = 200;




#include <AccelStepper.h>
AccelStepper stepper(AccelStepper::DRIVER, stepPin, dirPin);

#include "Vrekrer_scpi_parser.h"
#define FIRMWARE_VERSION "1.1.0" // Firmware version
SCPI_Parser command_parser;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(baudrate);
  pinMode(bouncerPin, INPUT_PULLUP);

  stepper.setEnablePin(enablePin);
  stepper.setCurrentPosition(-1);

  command_parser.RegisterCommand("*IDN?", &scpiSendID);
  
  command_parser.SetCommandTreeBase("SYSTem");
  command_parser.RegisterCommand(":HOme", &scpiHomeSearch);
  command_parser.RegisterCommand(":STAte?", &scpiSendDeviceState);
  
  command_parser.SetCommandTreeBase("MOve");
  command_parser.RegisterCommand(":RELative#", &scpiMoveRelative);
  command_parser.RegisterCommand(":ABSolute#", &scpiMoveAbsolute);
  command_parser.RegisterCommand(":POSition#", &scpiMoveAbsolute);
  command_parser.RegisterCommand(":POSition?", &scpiSendPosition);
  

}

void loop() {
  // put your main code here, to run repeatedly:

}

void sendCurrentPosition()
{
  long pos = stepper.currentPosition();
  if(pos == -1)
  {
    Serial.println("NONE");
  }else{
    Serial.println((float) pos * screwPitch / stepsPerRevolution);
  }
}

void homeSearch()
{
  while(digitalRead(bouncerPin))
  {
    stepper.move(-1);
  }
  stepper.move(1);
  stepper.setCurrentPosition(0);
}

void moveAbsolute(float value)
{
  if(stepper.currentPosition() != -1 and value > 0)
  {
    long pos = value / screwPitch * stepsPerRevolution;
    stepper.moveTo(pos);
  }
}

void moveRelative(float value)
{
  if(stepper.currentPosition() != -1)
  {
    long steps = value * screwPitch / stepsPerRevolution;
    if(stepper.currentPosition() + steps >= 0)
    {
      stepper.move(steps);
    }
  }
}

//SCPI commands
void scpiSendID(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  char idn[] = "STEPDUINO,001,001,"FIRMWARE_VERSION;
  Serial.println(idn);
}

void scpiHomeSearch(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  homeSearch();
}

void scpiSendDeviceState(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  Serial.println("state");
}

void scpiMoveRelative(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[REL]%u", &suffix);
  moveRelative(suffix);
}

void scpiMoveAbsolute(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  String header = String(commands.Last());
  header.toUpperCase();
  int suffix = -1;
  sscanf(header.c_str(),"%*[ABS]%u", &suffix);
  moveAbsolute(suffix);
}

void scpiSendPosition(SCPI_Commands commands, SCPI_Parameters parameters, Stream &interface)
{
  float pos = stepper.currentPosition() * screwPitch / stepsPerRevolution;
  Serial.println(pos);
}
