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
}

String getArrStr(){
  String stringFinal;
  
  String stringArr[] = {",","M:","LD:","RD:","UD:","DD:","Sq:","Tr:","Ci:","Xx:","Sh:","Op:","Ps:","L3:","R3:"};

  stringFinal = stringArr[0] + joystickArr[0] + stringArr[0] + joystickArr[1] + stringArr[0] + joystickArr[2] + stringArr[0] + joystickArr[3] + stringArr[0] + joystickArr[4] + stringArr[0] + joystickArr[5] + stringArr[0] + 
  stringArr[1] + runningMode + stringArr[0] + stringArr[2] + dpadArr[0] + stringArr[0] + stringArr[3] + dpadArr[1] + stringArr[0] + stringArr[4] + dpadArr[2] + stringArr[0] + stringArr[5] + dpadArr[3] + stringArr[0] + 
  stringArr[6] + shapeButtonArr[0] + stringArr[0] + stringArr[7] + shapeButtonArr[1] + stringArr[0] + stringArr[8] + shapeButtonArr[2] + stringArr[0] + stringArr[9] + shapeButtonArr[3] + stringArr[0] + 
  stringArr[10] + miscButtonArr[0] + stringArr[0] + stringArr[11] + miscButtonArr[1] + stringArr[0] + stringArr[12] + miscButtonArr[2] + stringArr[0] + stringArr[13] + miscButtonArr[3] + stringArr[0] + stringArr[14] + miscButtonArr[4];
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

//Main loop to be executed
void loop() {
  String readStr = Serial.readString();               //Read the serial line and set to readStr
  readStr.trim();                                     //Remove any \r \n whitespace at the end of the String
  readStr = rmPadStr(readStr);                        //Remove any padding from readStr
  if (readStr != ""){                                 //readStr == "" if the serial read had nothing in it
    //,1.000,1.000,1.000,1.000,1.000,1.000,M:0,LD:0,RD:0,UD:0,DD:0,Sq:0,Tr:0,Ci:0,Xx:0,Sh:0,Op:0,Ps:0,L3:0,R3:0
    for(int i = 0; i < 6; i++){ //get the joystickArr values
      joystickArr[i] = readStr.substring(1+(i*6),6+(i*6)).toFloat()-1; //0 = L3LR, 1 = L3UD, 2 = Triggers, 3 = R3LR, 4 = R3UD
    }
    runningMode = readStr.substring(39,40).toInt(); //get the mode (int)
    for(int i = 0; i < 4; i++){ //get the dpadArr values L,R,U,D (int)
      dpadArr[i] = readStr.substring(44+(i*5),45+(i*5)).toInt();
    }
    for(int i = 0; i < 4; i++){ //get the shapeButtonArr values Sq, Tr, Cir, X (int)
      shapeButtonArr[i] = readStr.substring(64+(i*5),65+(i*5)).toInt();
    }
    for(int i = 0; i < 5; i++){ //get the miscButtonArr values Share, Options, PS, L3, R3 (int)
      miscButtonArr[i] = readStr.substring(84+(i*5),85+(i*5)).toInt();
    }
    Serial.println(getArrStr());
//    Serial.println(readStr);
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
