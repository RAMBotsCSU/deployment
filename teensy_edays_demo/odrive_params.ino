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
int encoderParamNum = 12;

void getOdriveParams (HardwareSerial& s) {
  String axis = "axis1";
  Serial.println("In Get odrive params");
  for (int i=0; i < encoderParamNum; i++) {
    String command = axis + ".encoder.config." + encoderParams[i];
    Serial.print(command + " ");
    s << formatStr(command);
    String val = odrive2.readFloat();
    Serial.println(val);
  }
  // Serial.print(readParamStr("axis0.encoder.config.use_index_offset"));
  // s << formatStr("axis0.encoder.config.use_index_offset");
  // String cpr = odrive2.readFloat();
  // Serial.println(cpr);
}

String formatStr(String str){
  return "r " + str + " \n";
}

void getAxisParams (int axis_num) {

}