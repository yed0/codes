#include "GyverMotor.h"

// Pin definitions for the motors (adjust according to your setup)
GMotor motorL(DRIVER2WIRE, 5, 4, HIGH);  // Left motor: Pins 4 (EN, LPWM_L), 5 (PWM, RPWM_L)
GMotor motorR(DRIVER2WIRE, 2, 3, HIGH);  // Right motor: Pins 2 (EN, LPWM_R), 3 (PWM, RPWM_R)
int svet = 53;
int motorstrela1=44;
int motorstrela2=45;
int flag=1;
void setup() {
  // Start serial communication at 9600 baud rate
  Serial.begin(9600);
  
  // Initialize motors (ensure both are stopped initially) 
  motorL.setMinDuty(100);
  motorR.setMinDuty(100);
  motorL.setMode(FORWARD);
  motorR.setMode(FORWARD);

  pinMode(motorstrela1, OUTPUT); pinMode(motorstrela2, OUTPUT);
  pinMode(svet, OUTPUT);

  Serial.println("Ready for serial commands.");
}

  void loop() {
  digitalWrite(svet, 1);
  //if (flag==1){
    //analogWrite(motorstrela1, 100);
    //analogWrite(motorstrela2, 0);
    //delay(700);
    //analogWrite(motorstrela1, 0);
    //analogWrite(motorstrela2, 0);
    //flag=0;
  //}
  // Check if data is available on the serial port
  if (Serial.available() > 0) {
    // Read the incoming serial command
    char command = Serial.read();
    
    // Control motors based on the received command
    switch (command) {
      case 'F':  // Forward
        moveForward();
        break;
      case 'B':  // Backward
        moveBackward();
        break;
      case 'L':  // Left
        turnLeft();
        break;
      case 'R':  // Right
        turnRight();
        break;
      case 'S':  // Stop
        stopMotors();
        break;
      default:
        Serial.println("Invalid command");
        break;
    }
  }
}

// Function to move forward
void moveForward() {
  motorL.setSpeed(20);  // Full speed forward
  motorR.setSpeed(20);  // Full speed forward
  Serial.println("Moving forward");
}

// Function to move backward
void moveBackward() {
  motorL.setSpeed(-20);  // Full speed backward
  motorR.setSpeed(-20);  // Full speed backward
  Serial.println("Moving backward");
}

// Function to turn left
void turnLeft() {
  motorL.setSpeed(-20);  // Left motor backward
  motorR.setSpeed(20);   // Right motor forward
  Serial.println("Turning left");
}

// Function to turn right
void turnRight() {
  motorL.setSpeed(20);   // Left motor forward
  motorR.setSpeed(-20);  // Right motor backward
  Serial.println("Turning right");
}

// Function to stop the motors
void stopMotors() {
  motorL.setSpeed(0);  // Stop left motor
  motorR.setSpeed(0);  // Stop right motor
  Serial.println("Motors stopped");
}

