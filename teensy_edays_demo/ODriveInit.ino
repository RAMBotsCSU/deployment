  //**************************************************************************
  //* File takes in data from odrives. Finds new offsets and sends info back *
  //* to Odrives all utilizing serial bus                                    *
  //**************************************************************************

float offSet10 = -0.5;      //ODrive 1, axis 0     // hips - right front
float offSet11 = 0.45;      //ODrive 1, axis 1     // hips - right back
float offSet40 = 0.45;      //ODrive 4, axis 0     // hips - left front
float offSet41 = 0.15;      //ODrive 4, axis 1     // hips - left back

float offSet21 = -0.35;      //ODrive 2, axis 1     // shoulder - right front // Positive Increment = shoulder forward
float offSet31 = 0.0;       //ODrive 3, axis 1     // shoulder - right rear // Positive increment = shoulder forward
float offSet51 = 0.8;       //ODrive 5, axis 0     // shoulder - left front // Positive Increment = shoulder back
float offSet61 =  -0.9;     //ODrive 6, axis 1     // shoulder - left rear // Positive increment = shoulder back

float offSet20 = -1.5;      //ODrive 2, axis 0     // knee - right front // Positive Increment = knee backward
float offSet30 = 0.8;       //ODrive 3, axis 0     // knee - right rear // Positive Increment = knee forward
float offSet50 = 1.22;      //ODrive 5, axis 0     // knee - left front
float offSet60 = -1.1;      //ODrive 6, axis 0     // knee - left rear // Positive Increment = knee forward

void modifyGains() {  // this function turns up the gains when it is executed (menu option 4 via the remote)
  float posGainKnee = 20.0;
  float posGainHips = 60.0;
  float posGainShoulder = 20.0;
  float velGain = 0.1;
  float integrator = 0.2;

  Serial1 << "w axis" << 0 << ".controller.config.pos_gain " << posGainHips << '\n';
  Serial1 << "w axis" << 1 << ".controller.config.pos_gain " << posGainHips << '\n';

  Serial2 << "w axis" << 0 << ".controller.config.pos_gain " << posGainKnee << '\n';
  Serial2 << "w axis" << 1 << ".controller.config.pos_gain " << posGainShoulder << '\n';

  Serial3 << "w axis" << 0 << ".controller.config.pos_gain " << posGainKnee << '\n';
  Serial3 << "w axis" << 1 << ".controller.config.pos_gain " << posGainShoulder << '\n';

  Serial4 << "w axis" << 0 << ".controller.config.pos_gain " << posGainHips << '\n';
  Serial4 << "w axis" << 1 << ".controller.config.pos_gain " << posGainHips << '\n';

  Serial5 << "w axis" << 0 << ".controller.config.pos_gain " << posGainKnee << '\n';
  Serial5 << "w axis" << 1 << ".controller.config.pos_gain " << posGainShoulder << '\n';

  Serial6 << "w axis" << 0 << ".controller.config.pos_gain " << posGainKnee << '\n';
  Serial6 << "w axis" << 1 << ".controller.config.pos_gain " << posGainShoulder << '\n';

  // ******

  Serial1 << "w axis" << 0 << ".controller.config.vel_gain " << velGain << '\n';
  Serial1 << "w axis" << 1 << ".controller.config.vel_gain " << velGain << '\n';

  Serial2 << "w axis" << 0 << ".controller.config.vel_gain " << velGain << '\n';
  Serial2 << "w axis" << 1 << ".controller.config.vel_gain " << velGain << '\n';

  Serial3 << "w axis" << 0 << ".controller.config.vel_gain " << velGain << '\n';
  Serial3 << "w axis" << 1 << ".controller.config.vel_gain " << velGain << '\n';

  Serial4 << "w axis" << 0 << ".controller.config.vel_gain " << velGain << '\n';
  Serial4 << "w axis" << 1 << ".controller.config.vel_gain " << velGain << '\n';

  Serial5 << "w axis" << 0 << ".controller.config.vel_gain " << velGain << '\n';
  Serial5 << "w axis" << 1 << ".controller.config.vel_gain " << velGain << '\n';

  Serial6 << "w axis" << 0 << ".controller.config.vel_gain " << velGain << '\n';
  Serial6 << "w axis" << 1 << ".controller.config.vel_gain " << velGain << '\n';

  // ******

  Serial1 << "w axis" << 0 << ".controller.config.vel_integrator_gain " << integrator << '\n';
  Serial1 << "w axis" << 1 << ".controller.config.vel_integrator_gain " << integrator << '\n';

  Serial2 << "w axis" << 0 << ".controller.config.vel_integrator_gain " << integrator << '\n';
  Serial2 << "w axis" << 1 << ".controller.config.vel_integrator_gain " << integrator << '\n';

  Serial3 << "w axis" << 0 << ".controller.config.vel_integrator_gain " << integrator << '\n';
  Serial3 << "w axis" << 1 << ".controller.config.vel_integrator_gain " << integrator << '\n';

  Serial4 << "w axis" << 0 << ".controller.config.vel_integrator_gain " << integrator << '\n';
  Serial4 << "w axis" << 1 << ".controller.config.vel_integrator_gain " << integrator << '\n';

  Serial5 << "w axis" << 0 << ".controller.config.vel_integrator_gain " << integrator << '\n';
  Serial5 << "w axis" << 1 << ".controller.config.vel_integrator_gain " << integrator << '\n';

  Serial6 << "w axis" << 0 << ".controller.config.vel_integrator_gain " << integrator << '\n';
  Serial6 << "w axis" << 1 << ".controller.config.vel_integrator_gain " << integrator << '\n';
}

void driveJoints(int joint, float pos) {
  // takes into account the original setup offsets for motor postions, and also turns around directions so they are consistent
  // also constrains the motion limts for each joint

  //if (mydata_remote.toggleTop == 1) {       // ************** only do it if the motor enable is on via teh remote *****************

  // knees

  if (joint == 20) {
      pos = constrain(pos, -2.5,2.5);
      odrive2.SetPosition(0, pos + offSet20);    // knee - right front
  }
  else if (joint == 30) {
      pos = constrain(pos, -2.5,2.5);
      odrive3.SetPosition(0, (pos*-1) + offSet30);    // knee - right back
  }
  else if (joint == 50) {
      pos = constrain(pos, -2.5,2.5);
      odrive5.SetPosition(0, (pos*-1) + offSet50);    // knee - left front
  }
  else if (joint == 60) {
      pos = constrain(pos, -2.5,2.5);
      odrive6.SetPosition(0, pos + offSet60);    // knee - left back
  }

  // shoulder

  else if (joint == 21) {
      pos = constrain(pos, -2.5,2.5);
      odrive2.SetPosition(1, (pos*-1) + offSet21);    // shoulder - right front
  }
  else if (joint == 31) {
      pos = constrain(pos, -2.5,2.5);
      odrive3.SetPosition(1, pos + offSet31);    // shoulder - right rear
  }
  else if (joint == 51) {
      pos = constrain(pos, -2.5,2.5);
      odrive5.SetPosition(1, pos + offSet51);    // shoulder - left front
  }
  else if (joint == 61) {
      pos = constrain(pos, -2.5,2.5);
      odrive6.SetPosition(1, (pos*-1) + offSet61);    // shoulder - left rear
  }

  // hips
  else if (joint == 10) {
      pos = constrain(pos, -2.5,2.5);
      //delay(5000);
      odrive1.SetPosition(0, pos + offSet10); //----------minus: hip out    pos: hip in
      //odrive1.SetPosition(0, pos+offSet10);    // hips - right front
      delay(5);
  }
  else if (joint == 11) {
      pos = constrain(pos, -2.5,2.5);
      odrive1.SetPosition(1, (pos*-1) + offSet11);    // hips - right rear
  }
  else if (joint == 40) {
      pos = constrain(pos, -2.5,2.5);
      odrive4.SetPosition(0, pos + offSet40);    // hips - knee - left front
  }
  else if (joint == 41) {
      pos = constrain(pos, -2.5,2.5);
      odrive4.SetPosition(1, (pos*-1) + offSet41);    // hips - left rear
  }
}
