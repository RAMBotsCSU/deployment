//********************************************************
//* This is a simple test for the teensy that recieves   *
//* a string over the serial line, appends some values   *
//* then sends it back over serial. This method includes *
//* padding functions for the serial communication to    *
//* speed up the communication.                          *
//********************************************************

// ramp lib
#include <Ramp.h>
#include <ODriveArduino.h>
#include <HardwareSerial.h>

//Setup and set the pin for the LED
int led = 13;
int setInd = -1;
float setVal = -1.1;
float movementArr[7]; //0 = strafe, 1 = forback, 2 = roll, 3 = turn, 4 = pitch, 5 = height, 6 = yaw
String keyWord = "00";



int interpFlag = 0;
long previousInterpMillis = 0;    // set up timers

unsigned long currentMillis;
long previousMillis = 0;    // set up timers
long interval = 10;        // time constant for timer
unsigned long count;
int toggleTopOld;
int remoteState;
int remoteStateOld;  

int requested_state;
int mode;
int modeOld;
int modeFlag;
int menuFlag;
int modeConfirm;
int modeConfirmFlag = 0;
int runMode = 0;

// Printing with stream operator
template<class T> inline Print& operator <<(Print &obj,     T arg) { obj.print(arg);    return obj; }
template<>        inline Print& operator <<(Print &obj, float arg) { obj.print(arg, 4); return obj; }





// ODrive offsets from power up
// ratio is 10:1 so 1 'turn' is 36'.


float offSet20 = -0.3;      //ODrive 2, axis 0     // knee - right front
float offSet30 = 0.6;      //ODrive 3, axis 0     // knee - right rear
float offSet50 = 0.15;      //ODrive 5, axis 0     // knee - left front
float offSet60 = 0.05;      //ODrive 6, axis 0     // knee - left rear

float offSet21 = 0;      //ODrive 2, axis 1     // shoulder - right front
float offSet31 = 0.35;      //ODrive 3, axis 1     // shoulder - right rear
float offSet51 = 0.55;      //ODrive 5, axis 0     // shoulder - left front
float offSet61 =  0.05;      //ODrive 6, axis 1     // shoulder - left rear

float offSet10 = 0.27;      //ODrive 1, axis 0     // hips - right front
float offSet11 = 0.1;      //ODrive 1, axis 1     // hips - right back
float offSet40 = 0.07;      //ODrive 4, axis 0     // hips - left front
float offSet41 = 0.35;      //ODrive 4, axis 1     // hips - left back

HardwareSerial& odrive1Serial = Serial1;
HardwareSerial& odrive2Serial = Serial2;
HardwareSerial& odrive3Serial = Serial3;
HardwareSerial& odrive4Serial = Serial4;
HardwareSerial& odrive5Serial = Serial5;
HardwareSerial& odrive6Serial = Serial6;

//ODrive Objects
ODriveArduino odrive1(odrive1Serial);
ODriveArduino odrive2(odrive2Serial);
ODriveArduino odrive3(odrive3Serial);
ODriveArduino odrive4(odrive4Serial);
ODriveArduino odrive5(odrive5Serial);
ODriveArduino odrive6(odrive6Serial);

ODriveArduino odrArr[6] = {odrive1, odrive2, odrive3, odrive4, odrive5, odrive6};

void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
  odrive1Serial.begin(115200);
  odrive2Serial.begin(115200);
  odrive3Serial.begin(115200);
  odrive4Serial.begin(115200);
  odrive5Serial.begin(115200);
  odrive6Serial.begin(115200);
  //Serial7.begin(115200);

  odrive1Serial.print("sr\n");
  odrive2Serial.print("sr\n");
  //odrive3Serial.print("sr\n");
  //odrive4Serial.print("sr\n");
  //odrive5Serial.print("sr\n");
  //odrive6Serial.print("sr\n");

  int closedLoop = 8;
  for (int i = 0; i<2; i++){
    for (int axis = 0; axis<2; axis++){ //each axis in the odrive
      float indexFound = 0;
      float found = 0;
      while (found == 0){
        indexFound = odrArr[i].IndexFound(axis);
        if (indexFound > 0.){
          found = 1;
          delay(5);
          odrArr[i].run_state(axis,closedLoop, false);
          //Serial.print(i);
          //Serial.println(axis);
        }
      }
    } 
  }
}

String getArrStr(){
  String stringFinal;
  String String1 = "Teensy: strafe:";
  String String2 = ", forback:";
  String String3 = ", roll:";
  String String4 = ", turn:";
  String String5 = ", pitch:";
  String String6 = ", height:";
  String String7 = ", yaw:";
  double Val1 = movementArr[0];
  double Val2 = movementArr[1];
  double Val3 = movementArr[2];
  double Val4 = movementArr[3];
  double Val5 = movementArr[4];
  double Val6 = movementArr[5];
  double Val7 = movementArr[6];

  stringFinal = String1 + Val1 + String2 + Val2 + String3 + Val3 + String4 + Val4 + String5 + Val5 + String6 + Val6 + String7 + Val7;
  return stringFinal;
  
}

//Function to pad the string to 120 chars (serial uses 127, but the write command adds 7 chars)
String padStr(String str){
  int target = 120-str.length();
  for (int i = 0; i < target; i++) {
    str += "~";
  }
  return str;
}

//Function to remove the padding of strings
String rmPadStr(String str){
  for (int i = 0; i < str.length(); i++){
    if (str[i] == '~'){
      str.remove(i);
      return str;
    }
  }
  return str;
}


class Interpolation {
  public:
    rampInt myRamp;
    int interpolationFlag = 0;
    int savedValue;

    int go(int input, int duration) {

      if (input != savedValue) {   // check for new data
        interpolationFlag = 0;
      }
      savedValue = input;          // bookmark the old value

      if (interpolationFlag == 0) {                                        // only do it once until the flag is reset
        myRamp.go(input, duration, LINEAR, ONCEFORWARD);              // start interpolation (value to go to, duration)
        interpolationFlag = 1;
      }

      int output = myRamp.update();
      return output;
    }
};    // end of class

Interpolation interpFRX;        // interpolation objects
Interpolation interpFRY;
Interpolation interpFRZ;
Interpolation interpFRT;

Interpolation interpFLX;        // interpolation objects
Interpolation interpFLY;
Interpolation interpFLZ;
Interpolation interpFLT;

Interpolation interpBRX;        // interpolation objects
Interpolation interpBRY;
Interpolation interpBRZ;
Interpolation interpBRT;

Interpolation interpBLX;        // interpolation objects
Interpolation interpBLY;
Interpolation interpBLZ;
Interpolation interpBLT;

/*
void updateMovement(){
  kinematics(1,0,0,0,0,0,0,0,0);
  kinematics(2,0,0,0,0,0,0,0,0);
  kinematics(3,0,0,0,0,0,0,0,0);
  kinematics(4,0,0,0,0,0,0,0,0);
}
*/
void testMovement(){
  float pos0 = odrive1.GetPosition(0);
  float pos1 = odrive1.GetPosition(1);
  float pos2 = odrive2.GetPosition(0);
  float pos3 = odrive2.GetPosition(1);
  
  odrive1.SetPosition(0,0);
  odrive1.SetPosition(1,0);
  odrive2.SetPosition(0,0);
  odrive2.SetPosition(1,0);
  delay(1000);
  
  odrive1.SetPosition(0,0.1);
  odrive1.SetPosition(1,0.1);
  odrive2.SetPosition(0,0.1);
  odrive2.SetPosition(1,0.1);
  delay(100);

  odrive1.SetPosition(0,0.2);
  odrive1.SetPosition(1,0.2);
  odrive2.SetPosition(0,0.2);
  odrive2.SetPosition(1,0.2);
  delay(100);

  odrive1.SetPosition(0,0.3);
  odrive1.SetPosition(1,0.3);
  odrive2.SetPosition(0,0.3);
  odrive2.SetPosition(1,0.3);
  delay(100);

  odrive1.SetPosition(0,0.4);
  odrive1.SetPosition(1,0.4);
  odrive2.SetPosition(0,0.4);
  odrive2.SetPosition(1,0.4);
  delay(100);

  odrive1.SetPosition(0,0.5);
  odrive1.SetPosition(1,0.5);
  odrive2.SetPosition(0,0.5);
  odrive2.SetPosition(1,0.5);
  delay(100);

  odrive1.SetPosition(0,0.4);
  odrive1.SetPosition(1,0.4);
  odrive2.SetPosition(0,0.4);
  odrive2.SetPosition(1,0.4);
  delay(100);

  odrive1.SetPosition(0,0.3);
  odrive1.SetPosition(1,0.3);
  odrive2.SetPosition(0,0.3);
  odrive2.SetPosition(1,0.3);
  delay(100);

  odrive1.SetPosition(0,0.2);
  odrive1.SetPosition(1,0.2);
  odrive2.SetPosition(0,0.2);
  odrive2.SetPosition(1,0.2);
  delay(100);

  odrive1.SetPosition(0,0.1);
  odrive1.SetPosition(1,0.1);
  odrive2.SetPosition(0,0.1);
  odrive2.SetPosition(1,0.1);
  delay(100);/*
  kinematics(1,0,0,350,0,0,0,0,1000);
  delay (5000);
  kinematics(1,0,0,240,0,0,0,0,1000);
  */
 /*
  kinematics(1,0,0,350,0,0,0,0,0);
  kinematics(2,0,0,240,0,0,0,0,0);
  kinematics(3,0,0,350,0,0,0,0,0);
  kinematics(4,0,0,240,0,0,0,0,0);

  kinematics(1,0,0,240,0,0,0,0,0);
  kinematics(2,0,0,350,0,0,0,0,0);
  kinematics(3,0,0,240,0,0,0,0,0);
  kinematics(4,0,0,350,0,0,0,0,0);

  kinematics(1,0,0,350,0,0,0,0,0);
  kinematics(2,0,0,350,0,0,0,0,0);
  kinematics(3,0,0,350,0,0,0,0,0);
  kinematics(4,0,0,350,0,0,0,0,0);
 */
}

//Main loop to be executed
void loop() {
 currentMillis = millis();

  if (currentMillis - previousMillis >= 10) {  // start timed event

    previousMillis = currentMillis;

      remoteState = 1;
    }    


  
  digitalWrite(led, LOW);                             //Set LED to off when no message has been recieved
  //while (Serial.available() == 0) {}                //optional wait for serial input
  String readStr = Serial.readString();               //Read the serial line and set to readStr
  readStr.trim();                                     //Remove any \r \n whitespace at the end of the String
  readStr = rmPadStr(readStr);                        //Remove any padding from readStr
  if (readStr != ""){                                 //readStr == "" if the serial read had nothing in it
    digitalWrite(led, HIGH);                          //Turn on the LED to show that a string with != "" has been recieved
    keyWord = readStr.substring(0,2);
    if (keyWord == "AR"){
      setInd = (readStr.substring(readStr.indexOf("R")+1,readStr.indexOf(":"))).toInt();
      setVal = (readStr.substring(readStr.indexOf(":")+1,readStr.indexOf(","))).toFloat();
      movementArr[setInd] = setVal;
      Serial.println(padStr(getArrStr()));      //Print to the serial buffer
    }
    else if (keyWord == "SQ"){
      testMovement();
      Serial.println(padStr("Test Complete"));
    }
  }
  //updateMovement();
  }
