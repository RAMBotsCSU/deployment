#ifndef CONFIG_H
#define CONFIG_H

// LEFT FRONT LEG
float offSet40 = 0.44;     // HIP      ODrive 4, axis 0     + = backward
float offSet51 = 0.7;      // SHOULDER ODrive 5, axis 0     + = backward
float offSet50 = 0.9;      // KNEE     ODrive 5, axis 0     + = forward

// LEFT BACK LEG
float offSet41 = 0.11;      // HIP      ODrive 4, axis 1    + = backward
float offSet61 =  -0.8;     // SHOULDER ODrive 6, axis 1    + = backward
float offSet60 = -0.7;      // KNEE     ODrive 6, axis 0    + = forward

// RIGHT FRONT LEG
float offSet10 = -0.55;     // HIP      ODrive 1, axis 0    + = forward
float offSet21 = -0.2;      // SHOULDER ODrive 2, axis 1    + = forward
float offSet20 = -1.3;      // KNEE     ODrive 2, axis 0    + = backward

// RIGHT BACK LEG
float offSet11 = 0.496;     // HIP      ODrive 1, axis 1    + = forward
float offSet31 = 0.95;      // SHOULDER ODrive 3, axis 1    + = forward
float offSet30 = 0.5;       // KNEE     ODrive 3, axis 0    + = backward

#endif