  //**************************************************************************
  //* File takes in data from odrives. Finds new offsets and sends info back *
  //* to Odrives all utilizing serial bus                                    *
  //**************************************************************************

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
      odrive2.SetPosition(0, pos - 0.60);    // knee - right front
  }
  else if (joint == 30) {
      pos = constrain(pos, -2.5,2.5);
      odrive3.SetPosition(0, (pos*-1) + offSet30);    // knee - right back
  }
  else if (joint == 50) {
      pos = constrain(pos, -2.5,2.5);
      odrive5.SetPosition(0, (pos*-1) + 1.22);    // knee - left front
  }
  else if (joint == 60) {
      pos = constrain(pos, -2.5,2.5);
      odrive6.SetPosition(0, pos - 0.69);    // knee - left back
  }
  
  // shoulder
  
  else if (joint == 21) {
      pos = constrain(pos, -2.5,2.5);
      odrive2.SetPosition(1, (pos*-1) - 0.36);    // shoulder - right front
  }        
  else if (joint == 31) {
      pos = constrain(pos, -2.5,2.5);
      odrive3.SetPosition(1, pos + offSet31);    // shoulder - right rear
  }        
  else if (joint == 51) {
      pos = constrain(pos, -2.5,2.5);
      odrive5.SetPosition(1, pos - 0.17);    // shoulder - left front
  }        
  else if (joint == 61) {
      pos = constrain(pos, -2.5,2.5);
      odrive6.SetPosition(1, (pos*-1) - 0.495);    // shoulder - left rear      
  }
  
  // hips
  else if (joint == 10) {
      pos = constrain(pos, -2.5,2.5);
      //delay(5000);
      odrive1.SetPosition(0, pos-0.5); //----------minus: hip out    pos: hip in
      //odrive1.SetPosition(0, pos+offSet10);    // hips - right front 
      delay(5);
  }
  else if (joint == 11) {
      pos = constrain(pos, -2.5,2.5);
      odrive1.SetPosition(1, (pos*-1)+0.45);    // hips - right rear
  }
  else if (joint == 40) {
      pos = constrain(pos, -2.5,2.5);
      odrive4.SetPosition(0, pos+0.45);    // hips - knee - left front
  }
  else if (joint == 41) {
      pos = constrain(pos, -2.5,2.5);
      odrive4.SetPosition(1, (pos*-1)+0.15);    // hips - left rear
  }
}
