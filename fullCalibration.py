import odrive
import fibre.libfibre
import math
import time
import sys
import os
                                                #########################################
dev0 = odrive.find_any()                        # Find connected ODESC                  #
try:                                            #                                       #
    dev0.erase_configuration()                  # Erase config                          #
except fibre.libfibre.ObjectLostError:          # except that the ODESC will disconnect #
    pass                                        #########################################

                                                ###########################################
dev0 = odrive.find_any()                        # Refind ODESC                            #
ax0 = dev0.axis0                                # Simplified naming scheme for components #
ax1 = dev0.axis1                                ###########################################
mo0 = ax0.motor
mo1 = ax1.motor
enc0 = ax0.encoder
enc1 = ax1.encoder
contr0 = ax0.controller
contr1 = ax1.controller
                                                ##############################################################
mo0.config.pole_pairs = 20                      # Counted on motor (1/2 the number of magnets)               #
mo1.config.pole_pairs = 20                      #                                                            #
mo0.config.torque_constant = 0.025              # 8.27/90 was original, set lower to increase torque output  #
mo1.config.torque_constant = 0.025              #                                                            #
mo0.config.current_lim = 22                     # Max continuous current                                     #
mo1.config.current_lim = 22                     #                                                            #
mo0.config.current_lim_margin = 9               # Margin for max current that reached peak operating current #
mo1.config.current_lim_margin = 9               ##############################################################

                                                #####################################
contr0.config.pos_gain = 60                     # Gain values found from OpenDog v3 #
contr1.config.pos_gain = 60                     #                                   #
contr0.config.vel_gain = 0.1                    #                                   #
contr1.config.vel_gain = 0.1                    #                                   #
contr0.config.vel_integrator_gain = 0.2         #                                   #
contr1.config.vel_integrator_gain = 0.2         #                                   #
contr0.config.vel_limit = math.inf              # 500 without resistors             #
contr1.config.vel_limit = math.inf              #####################################

                                                ##############################
dev0.config.gpio7_mode = 0                      # Set pins to digital        #
dev0.config.gpio8_mode = 0                      #                            #
enc0.config.cpr = 16384                         # Has different value in SPI #
enc1.config.cpr = 16384                         #                            #
enc0.config.abs_spi_cs_gpio_pin = 7             # Set pins to SPI mode       #
enc1.config.abs_spi_cs_gpio_pin = 8             #                            #
enc0.config.mode = 257                          # Set encoder to SPI mode    #
enc1.config.mode = 257                          ##############################

try:
    dev0.save_configuration()
    dev0.reboot()
except fibre.libfibre.ObjectLostError:
    pass
dev0 = odrive.find_any()
ax0 = dev0.axis0
ax1 = dev0.axis1
mo0 = ax0.motor
mo1 = ax1.motor
enc0 = ax0.encoder
enc1 = ax1.encoder
contr0 = ax0.controller
contr1 = ax1.controller
dev0.clear_errors()

                                                #######################################
ax0.requested_state = 4                         # Motor 0 calibration                 #
while(not(mo0.is_calibrated)):                  #                                     #
    time.sleep(2)                               #                                     #
    print('motor 0 not calibrated')             #                                     #
    print(mo0.error)                            #                                     #
    print(enc0.error)                           #                                     #
mo0.config.pre_calibrated = True                # Pre-calibrate motor 0 for startup   #
                                                #                                     #
ax1.requested_state = 4                         # Motor 1 calibration                 #
while(not(mo1.is_calibrated)):                  #                                     #
    time.sleep(2)                               #                                     #
    print('motor 1 not calibrated')             #                                     #
    print(mo1.error)                            #                                     #
    print(enc1.error)                           #                                     #
mo1.config.pre_calibrated = True                # Pre-calibrate motor 1 for startup   #
                                                #                                     #
ax0.requested_state = 7                         # Encoder 0 calibration               #
while(not(enc0.is_ready)):                      #                                     #
    time.sleep(2)                               #                                     #
    print('encoder 0 not calibrated')           #                                     #
    print(mo0.error)                            #                                     #
    print(enc0.error)                           #                                     #
enc0.config.pre_calibrated = True               # Pre-calibrate encoder 0 for startup #
                                                #                                     #
ax1.requested_state = 7                         # Encoder 1 calibration               #
while(not(enc1.is_ready)):                      #                                     #
    time.sleep(2)                               #                                     #
    print('encoder 1 not calibrated')           #                                     #
    print(mo1.error)                            #                                     #
    print(enc1.error)                           #                                     #
enc1.config.pre_calibrated = True               # Pre-calibrate encoder 1 for startup #
                                                #######################################

                                                ###########################################################
dev0.config.enable_brake_resistor = True        # If have resistors (resistance is at 2 ohms per default) #
dev0.clear_errors()                             # Must do this to enable resistor                         #
ax0.config.startup_closed_loop_control = True   # Go into closed loop on restart                          #
ax1.config.startup_closed_loop_control = True   ###########################################################

try:                                            ###################################
    dev0.save_configuration()                   # Save config (will reboot ODESC) #
except fibre.libfibre.ObjectLostError:          ###################################
    pass
