# RamBOTs Deployment Repo
                   
This is the official CSU RAMBots Deployment repository, consisting of programs currently deployed on the robot. 
Visit us at our [website](https://projects-web.engr.colostate.edu/ece-sr-design/AY22/RamBOTs).

Based on OpenDogV3 by James Bruton. Original repository can be found [here](https://github.com/XRobots/openDogV3)

<img src="https://user-images.githubusercontent.com/112744753/196563382-2745e707-77d6-42d5-98a0-a29530e21c9a.png" width=50% height=50%>

License:
------

MIT License

Copyright (c) 2021 James Bruton

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Files:
------

| File        | Description           |
| ------------- |-------------|
| opendog_walk_cycle_demo | Directory for walking demo using opendog walking cycle |
| &emsp;opendog_walk_cycle_demo/pi_simple_controller.py      | Pi program to poll controller inputs and interface with openDog code on the Teensy|
| opendog_walk_cycle_demo/teensy_serial_main_opendog      | Teensy program implementing opendogV3 walk cycle  |
|       |  |
| rambots_serial_main | Directory for original Rambots Pi-Teensy serial communication programs |
| rambots_serial_main/pi_serial_main.py        |  Pi program to run controller and communicate high level movement to Teensy   |
| rambots_serial_main/color_test.sh        | Auxillary bash scripts to manage controller color |
| rambots_serial_main/teensy_serial_main       | Teensy program to convert high level movement commands from Pi to ODrive instructions |
