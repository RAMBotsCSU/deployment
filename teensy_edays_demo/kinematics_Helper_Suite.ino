// Printing with stream operator
//template<class T> inline Print& operator <<(Print &obj,     T arg) { obj.print(arg);    return obj; }
//template<>        inline Print& operator <<(Print &obj, float arg) { obj.print(arg, 4); return obj; }


void height_Test(int val){
  kinematics(1,0,0,val,0,0,0,0,0);
}

//Helper function to transistion from one location to the next
//Takes a leg number and the two and from positions for all of the directions
void transitionKinematics(int leg, float xFrom, float xTo, float yFrom, float yTo, float zFrom, float zTo){
  //Serial << "Moving Leg " << leg << " xFrom: " << xFrom << " xTo " << xTo << " yFrom: " << yFrom << " yTo " << yTo << " zFrom: " << zFrom << " zTo " << zTo << "\n";
  int maxDis = abs(xFrom-xTo); 
  float xStep, yStep, zStep;
  float xCur = xFrom;
  float yCur = yFrom;
  float zCur = zFrom;
  if(abs(yFrom-yTo)>maxDis){
    maxDis = abs(yFrom-yTo);
  }
  if(abs(zFrom-zTo)>maxDis){
    maxDis = abs(zFrom-zTo);
  }

  xStep = -1*(xFrom-xTo)/maxDis;
  yStep = -1*(yFrom-yTo)/maxDis;
  zStep = -1*(zFrom-zTo)/maxDis;
//  Serial << "xStep: " << xStep << " yStep: " << yStep << " zStep: " << zStep << "\n";
  for(int i=0; i <maxDis; i++){
    xCur = xCur+xStep;
    yCur = yCur+yStep;
    zCur = zCur+zStep;
    kinematics(leg,xCur,yCur,zCur,0,0,0,0,0);
    //Serial << "Just moved to x: " << xCur << " y: " << yCur << " z: " << zCur << "\n";
  }
  kinematics(leg,xTo,yTo,zTo,0,0,0,0,0);
  //Serial << "Final position" << " x " << xTo  << " y " << yTo << " z " << zTo << "\n";
   
}

void triangleWalk(int leg, float xDis, float yDis, float tallLeg, float shortLeg, int stepDelay){
  //forward, we go triangleupforward,down,back
  //kinematics(leg,walkMinH,walkInY,walkMaxH,0,0,0,0,0);
//  Serial.println("Up and out");
  transitionKinematics(leg, 0, xDis, 0, yDis, tallLeg, shortLeg);  
  delay(stepDelay);
//  Serial.println("Down");
  transitionKinematics(leg, xDis, xDis, yDis, yDis, shortLeg, tallLeg);
  delay(stepDelay);
//  Serial.println("In");
  transitionKinematics(leg, xDis, 0, yDis, 0, tallLeg, tallLeg);
  delay(stepDelay);
}
//Old function for triangular walking on leg 1 (depricated)
//Takes: dir (1: forward, -1: back), longLegLength, shortLegLength,
//XAwayFromBody, XIntoBody, YOffset, delay
//Set XIntoBody to 0 for a centered walk
//Traverses up and forward, down, back
void triangleWalkOld(int dir, float walkMaxH, float walkMinH, float walkMaxF, float walkMinF, float walkY, int stepDelay){
  walkMaxF = walkMaxF*-1;
  walkMinF = walkMinF*-1;
  double tempX = -1;
  Serial.println("Test Walk Triangle");
  Serial << "Dir: " << dir << " walkMaxH: " << walkMaxH << " walkMinH: " << walkMinH << " walkMaxF: " << walkMaxF << " walkMinF: " << walkMaxF << '\n';
  //Initial pos
  kinematics(1,dir*walkMinF,walkY,walkMaxH,0,0,0,0,0);
  //up and forward
  delay(stepDelay);
  tempX = dir*walkMinF;
  for (int i = walkMaxH; i>=walkMinH; i--){
    kinematics(1,tempX,walkY,i,0,0,0,0,0);
    //Serial << "Just moved to X: " << tempX << " Z: " << i << "\n";
    tempX = tempX+(dir*-1*(abs(walkMaxF-walkMinF)/abs(walkMaxH-walkMinH)));
  }
  //down
  delay(stepDelay);
  Serial.println("Going down");
  for (int i = walkMinH; i<=walkMaxH; i++){ //down
    kinematics(1,dir*walkMaxF,walkY,i,0,0,0,0,0);
    //Serial << "Just moved to Z: " << i << "\n";
  }
  //back
  delay(stepDelay);
  Serial.println("Going back");
  for (int i = walkMaxF; i<=walkMinF; i++){ //back
    kinematics(1,dir*i,walkY,walkMaxH,0,0,0,0,0);
    //Serial << "Just moved to X: " << i << "\n";
  }
}
