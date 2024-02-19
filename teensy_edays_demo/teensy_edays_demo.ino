//********************************************************************************
//* Something about this code                                                    *
//*                                                                              *
//* ODriveInit initializes the o-drives with offsets specific to the Rambot.     *
//*                                                                              *
//* Kinematics_Helper_Suite provides an alternative interpolation method         *
//* to James Bruton's.                                                           *
//********************************************************************************

#include <Ramp.h>
#include <ODriveArduino.h>
#include <HardwareSerial.h>
#include <Wire.h>
#include "config.h"

int maxLegHeight = 380;
int minLegHeight = 320;

//Setup and set the pin for the LED
int led = 13;

//Temp Variables for setting values
int tempInt1 = -1;
int tempInt2 = -1;
float tempFloat = -1.1;
long tempLong = 0;
String tempString = "-1";

//Actual variables
int runningMode = -1;
float joystickArr[6]; //0 = L3LR, 1 = L3UD, 2 = triggerL, 3 = R3LR, 4 = R3UD, 5 = triggerR
int dpadArr[4]; //L,R,U,D 1=pressed 0=not pressed
int shapeButtonArr[4]; //Sq, Tr, Cir, X 1=pressed 0=not pressed
int miscButtonArr[5]; //Share, Options, PS, L3, R3 1=pressed 0=not pressed
bool gainsFlag = true;
bool pauseFlag = true; //false means paused
bool pauseChangeFlag = true;


//Required variables for kinematics
int interpFlag = 0;
long previousInterpMillis = 0;    // set up timers

unsigned long currentMillis = 0;
long previousMillis = 0;    // set up timers
long interval = 10;        // time constant for timer
unsigned long count;
int toggleTopOld;
int remoteState;
int remoteStateOld;  

//gyro variables
float LegRollFiltered = 0;
float LegPitchFiltered = 0;
float RateRoll, RatePitch, RateYaw;
float RateCalibrationRoll, RateCalibrationPitch, RateCalibrationYaw;
int RateCalibrationNumber;
float AccX, AccY, AccZ;
float AngleRoll, AnglePitch;

float KalmanAngleRoll=0, KalmanUncertaintyAngleRoll=2*2;
float KalmanAnglePitch=0, KalmanUncertaintyAnglePitch=2*2;
float Kalman1DOutput[]={0,0};



// Printing with stream operator
template<class T> inline Print& operator <<(Print &obj,     T arg) { obj.print(arg);    return obj; }
template<>        inline Print& operator <<(Print &obj, float arg) { obj.print(arg, 4); return obj; }

//Serial Objects
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


void setup() {
  pinMode(led, OUTPUT);
  Serial.begin(9600);
  odrive1Serial.begin(115200);
  odrive2Serial.begin(115200);
  odrive3Serial.begin(115200);
  odrive4Serial.begin(115200);
  odrive5Serial.begin(115200);
  odrive6Serial.begin(115200);

  //gyro setup
    Wire.setClock(400000);
  Wire.begin();
  delay(50);
  Wire.beginTransmission(0x68); 
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();
  for (RateCalibrationNumber=0; RateCalibrationNumber<500; RateCalibrationNumber ++) {
    gyro_signals();
    RateCalibrationRoll+=RateRoll;
    RateCalibrationPitch+=RatePitch;
    RateCalibrationYaw+=RateYaw;
    delay(1);
  }
  RateCalibrationRoll/=500;
  RateCalibrationPitch/=500;
  RateCalibrationYaw/=500;
  modifyGains();

  // TEMP
  Serial.setTimeout(100);
}

String getArrStr(){
  String stringFinal;
  
  String stringArr[] = {",","M:","LD:","RD:","UD:","DD:","Sq:","Tr:","Ci:","Xx:","Sh:","Op:","Ps:","L3:","R3:"};

  stringFinal = String(joystickArr[0]) + stringArr[0] + joystickArr[1] + stringArr[0] + joystickArr[2] + stringArr[0] + joystickArr[3] + stringArr[0] + joystickArr[4] + stringArr[0] + joystickArr[5] + stringArr[0] + 
  stringArr[1] + runningMode + stringArr[0] + stringArr[2] + dpadArr[0] + stringArr[0] + stringArr[3] + dpadArr[1] + stringArr[0] + stringArr[4] + dpadArr[2] + stringArr[0] + stringArr[5] + dpadArr[3] + stringArr[0] + 
  stringArr[6] + shapeButtonArr[0] + stringArr[0] + stringArr[7] + shapeButtonArr[1] + stringArr[0] + stringArr[8] + shapeButtonArr[2] + stringArr[0] + stringArr[9] + shapeButtonArr[3] + stringArr[0] + 
  stringArr[10] + miscButtonArr[0] + stringArr[0] + stringArr[11] + miscButtonArr[1] + stringArr[0] + stringArr[12] + miscButtonArr[2] + stringArr[0] + stringArr[13] + miscButtonArr[3] + stringArr[0] + stringArr[14] + miscButtonArr[4] + '#';
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

const int BUFFER_SIZE = 300;
char buf[BUFFER_SIZE];

//Main loop to be executed
void loop() {
  getOdriveParams(Serial2);
  // check if data is available
  int rxlen = Serial.available(); // number of bytes available in Serial buffer
  
  if (rxlen > 10) {
    int rlen; // number of bytes to read
    if (rxlen > BUFFER_SIZE) // check if the data exceeds the buffer size
      rlen = BUFFER_SIZE;    // if yes, read BUFFER_SIZE bytes. The remaining will be read in the next time
    else
      rlen = rxlen;

    // read the incoming bytes:
    rlen = Serial.readBytesUntil('#', buf, BUFFER_SIZE);
    // Serial.println("Recieved");

    String readStr = buf;               //Read the serial line and set to readStr
    Serial.println(readStr);
  
  
    // readStr.trim();                                     //Remove any \r \n whitespace at the end of the String
    // readStr = rmPadStr(readStr);                        //Remove any padding from readStr
    if (readStr != ""){                                 //readStr == "" if the serial read had nothing in it
      // Joystick Values ///////////////////////////////////////////
      int j0Index = readStr.indexOf("J0:");
      joystickArr[0] = readStr.substring(j0Index+3,j0Index+8).toFloat() - 1;

      int j1Index = readStr.indexOf("J1:");
      joystickArr[1] = readStr.substring(j1Index+3,j1Index+8).toFloat() - 1;

      int j2Index = readStr.indexOf("J2:");
      joystickArr[2] = readStr.substring(j2Index+3,j2Index+8).toFloat() - 1;

      int j3Index = readStr.indexOf("J3:");
      joystickArr[3] = readStr.substring(j3Index+3,j3Index+8).toFloat() - 1;

      int j4Index = readStr.indexOf("J4:");
      joystickArr[4] = readStr.substring(j4Index+3,j4Index+8).toFloat() - 1;

      int j5Index = readStr.indexOf("J5:");
      joystickArr[5] = readStr.substring(j5Index+3,j5Index+8).toFloat() - 1;


      // D Pad Buttons ///////////////////////////////////////////

      int mIndex = readStr.indexOf("M:");
      runningMode = readStr.substring(mIndex+2,mIndex+3).toInt(); //get the mode (int)

      int ldIndex = readStr.indexOf("LD:");
      dpadArr[0] = readStr.substring(ldIndex+3,ldIndex+4).toInt();

      int rdIndex = readStr.indexOf("RD:");
      dpadArr[1] = readStr.substring(rdIndex+3,rdIndex+4).toInt();

      int udIndex = readStr.indexOf("UD:");
      dpadArr[2] = readStr.substring(udIndex+3,udIndex+4).toInt();

      int ddIndex = readStr.indexOf("DD:");
      dpadArr[3] = readStr.substring(ddIndex+3,ddIndex+4).toInt();


      // Shape Buttons ///////////////////////////////////////////

      int sqIndex = readStr.indexOf("Sq:");
      shapeButtonArr[0] = readStr.substring(sqIndex+3,sqIndex+4).toInt();

      int trIndex = readStr.indexOf("Tr:");
      shapeButtonArr[1] = readStr.substring(trIndex+3,trIndex+4).toInt();

      int ciIndex = readStr.indexOf("Ci:");
      shapeButtonArr[2] = readStr.substring(ciIndex+3,ciIndex+4).toInt();

      int xxIndex = readStr.indexOf("Xx:");
      shapeButtonArr[3] = readStr.substring(xxIndex+3,xxIndex+4).toInt();


      // Misc Buttons ///////////////////////////////////////////

      int shIndex = readStr.indexOf("Sh:");
      miscButtonArr[0] = readStr.substring(shIndex+3,shIndex+4).toInt();

      int opIndex = readStr.indexOf("Op:");
      miscButtonArr[1] = readStr.substring(opIndex+3,opIndex+4).toInt();

      int psIndex = readStr.indexOf("Ps:");
      miscButtonArr[2] = readStr.substring(psIndex+3,psIndex+4).toInt();

      int l3Index = readStr.indexOf("L3:");
      miscButtonArr[3] = readStr.substring(l3Index+3,l3Index+4).toInt();

      int r3Index = readStr.indexOf("R3:");
      miscButtonArr[4] = readStr.substring(r3Index+3,r3Index+4).toInt();

      Serial.println(getArrStr());
    }

    
  }

  if(shapeButtonArr[0]==1 && gainsFlag){
    modifyGains();
    gainsFlag = false;
  }
  if(miscButtonArr[2] == 1 && pauseChangeFlag == true){ //true chage flag means we can update the paused mode again
    //swap the pause flag
    pauseFlag = !pauseFlag; //false flag means the program is paused
    pauseChangeFlag = false;
  }
  else if(miscButtonArr[2] == 0 && pauseChangeFlag == false){
    pauseChangeFlag = true; //true flag means program is not paused
  }  

  currentMillis = millis();
  //Serial.println(miscButtonArr[2]);
  if ((currentMillis - previousMillis >= 10)){

    previousMillis = currentMillis;
    // runningMode = 1;
    if(pauseFlag){
      switch (runningMode) {
      case 0: // opendog walking cycle - white
        openDogWalkCycle(joystickArr[1],joystickArr[0],joystickArr[3],joystickArr[2],joystickArr[5],false);
        break;
      case 1: // push up mode - yellow
        pushUps(shapeButtonArr[3]);
        break;
      case 2: // left/right control - orange
        LRControl(joystickArr[0],joystickArr[1],joystickArr[2],joystickArr[3],joystickArr[4],joystickArr[5]);
        break;
      case 3: // gyro demo - dark blue
        gyro_demo(joystickArr[3],joystickArr[4]);
        break;
      case 4: // machine learning - purple
        look_up_or_down(joystickArr[2],joystickArr[5]);
        break;
      case 5: // dance - green
        danceMode(dpadArr[0],dpadArr[2],dpadArr[1],dpadArr[3]);
        break;
      default:
        // statements
        break;
      }
    }  
    delay(10);
  }
  updateGyro();
}
