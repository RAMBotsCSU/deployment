// includes
#include <HardwareSerial.h>
#include <ODriveArduino.h>
// Printing with stream operator helper functions
template<class T> inline Print& operator <<(Print &obj,     T arg) { obj.print(arg);    return obj; }
template<>        inline Print& operator <<(Print &obj, float arg) { obj.print(arg, 4); return obj; }

// Teensy 3 and 4 (all versions) - Serial1
// pin 0: RX - connect to ODrive TX
// pin 1: TX - connect to ODrive RX
// See https://www.pjrc.com/teensy/td_uart.html for other options on Teensy
HardwareSerial & odrive_serial = Serial1;

// ODrive object
ODriveArduino odrive(odrive_serial);

void setup() {
  // ODrive uses 115200 baud
  odrive_serial.begin(115200);
  odrive_serial << "sr\n";
  // Serial to PC
  Serial.begin(115200);
  while (!Serial) ; // wait for Arduino Serial Monitor to open

  Serial.println("ODriveArduino");
  Serial.println("Setting parameters...");

  // In this example we set the same parameters to both motors.
  // You can of course set them different if you want.
  // See the documentation or play around in odrivetool to see the available parameters
  for (int axis = 0; axis < 2; ++axis) {
    odrive_serial << "w axis" << axis << ".controller.config.vel_limit " << 500.0f << '\n';
    odrive_serial << "w axis" << axis << ".motor.config.current_lim " << 10.0f << '\n';
    // This ends up writing something like "w axis0.motor.config.current_lim 10.0\n"
  }

  Serial.println("Ready!");
  Serial.println("Send the character '0' or '1' to calibrate respective motor (you must do this before you can command movement)");
  Serial.println("Send the character 's' to exectue test move");
  Serial.println("Send the character 'b' to read bus voltage");
  Serial.println("Send the character 'p' to read motor positions in a 10s loop");
}

void loop() {
  //odrive.SetPosition(0, 1);
  //odrive.SetPosition(1, 1);
  if (Serial.available()) {
    char c = Serial.read();

    // Run calibration sequence
    if (c == '0' || c == '1') {
      int motornum = c-'0';
      int requested_state;
    }

    if (c == 'z') {
      odrive.SetPosition(0, 1);
      odrive.SetPosition(1, 1);
    }
    
    // Sinusoidal test move
    if (c == 's') {
      Serial.println("Executing test move");
      int pos = (odrive.GetPosition(0)+odrive.GetPosition(1))/2;
      for (float ph = acos(pos); ph < 6.28318530718f+acos(pos); ph += 0.01f) {
        float pos_m0 = 1.0f * cos(ph);
        float pos_m1 = 1.0f * cos(ph);
        odrive.SetPosition(0, pos_m0);
        odrive.SetPosition(1, pos_m1);
        delay(5);
      }
    }

    // Read bus voltage
    if (c == 'b') {
      odrive_serial << "r vbus_voltage\n";
      Serial << "Vbus voltage: " << odrive.readFloat() << '\n';
    }

    // print motor positions in a 10s loop
    if (c == 'p') {
      static const unsigned long duration = 10000;
      unsigned long start = millis();
      while(millis() - start < duration) {
        for (int motor = 0; motor < 2; ++motor) {
          Serial << odrive.GetPosition(motor) << '\t';
        }
        Serial << '\n';
      }
    }
  }
}
