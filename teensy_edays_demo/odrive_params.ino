void getOdriveParams (ODriveArduino& odrive, HardwareSerial& serial) {
  // Serial.println("In Get odrive params");

  getEncoderParams(odrive, serial, "axis0");
  getEncoderParams(odrive, serial, "axis1");

  // getMotorParams(odrive, serial, "axis0");
  // getMotorParams(odrive, serial, "axis1");
  
  getControllerParams(odrive, serial, "axis0");
  getControllerParams(odrive, serial, "axis1");
  // Serial.print(readParamStr("axis0.encoder.config.use_index_offset"));
  // s << formatStr("axis0.encoder.config.use_index_offset");
  // String cpr = odrive2.readFloat();
}

void getMotorParams(ODriveArduino& odrive, HardwareSerial& serial, String axis) {
  String motorParams[] = {"I_bus_hard_max",
                          "I_bus_hard_min",
                          "I_leak_max",
                          "R_wL_FF_enable",
                          "acim_autoflux_attack_gain",
                          "acim_autoflux_decay_gain",
                          "acim_autoflux_enable",
                          "acim_autoflux_min_Id",
                          "acim_gain_min_flux",
                          "bEMF_FF_enable",
                          "calibration_current",
                          "current_control_bandwidth",
                          "current_lim",
                          "current_lim_margin",
                          "dc_calib_tau",
                          "inverter_temp_limit_lower",
                          "inverter_temp_limit_upper",
                          "motor_type",
                          "phase_inductance",
                          "phase_resistance",
                          "pole_pairs",
                          "pre_calibrated",
                          "requested_current_range",
                          "resistance_calib_max_voltage",
                          "torque_constant",
                          "torque_lim"};
  int motorParamNum = 26;

  for (int i=0; i < motorParamNum; i++) {
    String piCommand = axis + " motor.config." + motorParams[i];
    String command = axis + ".motor.config." + motorParams[i];
    Serial.print(piCommand + " ");
    serial << formatStr(command);
    String val = odrive.readFloat();
    Serial.println(val);
  }
}

void getEncoderParams(ODriveArduino& odrive, HardwareSerial& serial, String axis) {

  String encoderParams[] = {"abs_spi_cs_gpio_pin", 
                          "bandwidth", 
                          "calib_range",
                          "calib_scan_distance", 
                          "calib_scan_omega", 
                          "cpr", 
                          "direction", 
                          "enable_phase_interpolation", 
                          "find_idx_on_lockin_only", 
                          "hall_polarity",
                          "hall_polarity_calibrated",
                          "ignore_illegal_hall_state",
                          "index_offset",
                          "mode",
                          "phase_offset",
                          "phase_offset_float",
                          "pre_calibrated",
                          "sincos_gpio_pin_cos",
                          "sincos_gpio_pin_sin",
                          "use_index",
                          "use_index_offset"
                          };
  int encoderParamNum = 21;

  for (int i=0; i < encoderParamNum; i++) {
    String piCommand = axis + " encoder.config." + encoderParams[i];
    String command = axis + ".encoder.config." + encoderParams[i];
    Serial.print(piCommand + " ");
    serial << formatStr(command);
    String val = odrive.readFloat();
    Serial.println(val);
  }
}

void getControllerParams(ODriveArduino& odrive, HardwareSerial& serial, String axis) {
  String controllerParams[] = {"axis_to_mirror",
                            "circular_setpoint_range",
                            "circular_setpoints",
                            "control_mode",
                            "electrical_power_bandwidth",
                            "enable_gain_scheduling",
                            "enable_overspeed_error",
                            "enable_torque_mode_vel_limit",
                            "enable_vel_limit",
                            "gain_scheduling_width",
                            "homing_speed",
                            "inertia",
                            "input_filter_bandwidth",
                            "input_mode",
                            "load_encoder_axis",
                            "mechanical_power_bandwidth",
                            "mirror_ratio",
                            "pos_gain",
                            "spinout_electrical_power_threshold",
                            "spinout_mechanical_power_threshold",
                            "steps_per_circular_range",
                            "torque_mirror_ratio",
                            "torque_ramp_rate",
                            "vel_gain",
                            "vel_integrator_gain",
                            "vel_integrator_limit",
                            "vel_limit",
                            "vel_limit_tolerance",
                            "vel_ramp_rate"};
  int controllerParamNum = 28;

  for (int i=0; i < controllerParamNum; i++) {
    String piCommand = axis + " controller.config." + controllerParams[i];
    String command = axis + ".controller.config." + controllerParams[i];
    Serial.print(piCommand + " ");
    serial << formatStr(command);
    String val = odrive.readFloat();
    Serial.println(val);
  }
}

String formatStr(String str){
  return "r " + str + " \n";
}