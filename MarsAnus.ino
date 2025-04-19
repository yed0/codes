#include "GyverMotor.h"
#include <Servo.h>
#include <DHT.h>
#include <TroykaMQ.h>
#define DHTPIN 52
DHT dht(DHTPIN, DHT11);
#define pinMQ2 A6
#define pinMQ135 A7
MQ2 mq2(pinMQ2);
MQ135 mq135(pinMQ135);
#define PIN_TRIG 31
#define PIN_ECHO 34
long duration, cm;
Servo myservo;
GMotor motorL(DRIVER2WIRE, 4, 5, HIGH);
GMotor motorR(DRIVER2WIRE, 2, 3, HIGH);
int moto1 = 44;
int moto2 = 45;
unsigned long counts;
unsigned long previousMillis;
void impulse(){
  counts++;
}
#define LOG_PERIOD 60000
void setup() {
  Serial.begin(9600);
  motorL.setMinDuty(100);
  motorR.setMinDuty(100);
  motorL.setMode(FORWARD);
  motorR.setMode(FORWARD);
  pinMode(10, INPUT);
  pinMode(11, INPUT);
  pinMode(30, INPUT);
  pinMode(26, OUTPUT);
  pinMode(28, OUTPUT);
  pinMode(22, OUTPUT);
  pinMode(24, OUTPUT);
  pinMode(moto1, OUTPUT);
  pinMode(moto2, OUTPUT);
  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  myservo.attach(12);
  dht.begin();
  mq2.calibrate();
  mq135.calibrate();
  counts = 0;
  pinMode(51, INPUT);
  attachInterrupt(digitalPinToInterrupt(51), impulse, FALLING);
}

void loop() {
  int LX = map(pulseIn(7 , HIGH), 1850, 1100, -255, 255);
  int LY = map(pulseIn(6 , HIGH), 1850, 1100, -255, 255);
  int svet = map(pulseIn(10 , HIGH), 1850, 1100, -1, 1);
  int serv = map(pulseIn(8, HIGH), 1850, 1100, 40, 120);
  int mot = map(pulseIn(9, HIGH), 1850, 1100, -100, 100);
  int s3 = map(pulseIn(11, HIGH), 1850, 1100, -1, 1);
  int dutyR = LY + LX;
  int dutyL = LY - LX;
  dutyR = constrain(dutyR, -100, 100);
  dutyL = constrain(dutyL, -100, 100);
  int light = analogRead(A4);
  if (mot>20){
    analogWrite(moto1, 150);
    analogWrite(moto2, 0);
  }
  else if (mot<-20){
    analogWrite(moto1, 0);
    analogWrite(moto2, 150);
  }
  else{
    analogWrite(moto1, 0);
    analogWrite(moto2, 0);
  }
  
  
  if (svet > 0) {
    
    myservo.write(serv);
    if (dutyR > 30 || dutyR < -30 || dutyL > 30 || dutyL < -30) {
      motorR.setSpeed(dutyR);
      motorL.setSpeed(dutyL);
    }
    else {
      motorR.setSpeed(0);
      motorL.setSpeed(0);
    }
  }
  else if (svet < 0){
    if (LX>100 && 20>LY>-20){
      digitalWrite(28, HIGH);
      digitalWrite(26, HIGH);
    }
    else if(LY < -100 && 20>LX>-20){
      digitalWrite(28, HIGH);
      digitalWrite(26, LOW); 
    }
    else if(LY > 100 && 20>LX>-20){
      digitalWrite(28, LOW);
      digitalWrite(26, HIGH);
    }
    else if (LX<-100 && 20>LY>-20){
      float h = dht.readHumidity();
      float t = dht.readTemperature();
      Serial.println("Temperature: " + String(t) + " *C ");
      Serial.println("Humidity: "+String(h)+" %\t ");
      Serial.println("Light: " + String(light));
      Serial.println("LPG: " + String(mq2.readLPG()) + "ppm");
      Serial.println("Methane: " + String(mq2.readMethane()) + "ppm");
      Serial.println("Smoke: " + String(mq2.readSmoke()) + "ppm");
      Serial.println("Hydrogen: " + String(mq2.readHydrogen()) + "ppm");
      Serial.println("CO2: " + String(mq135.readCO2()) + "ppm");
      Serial.println("UV: " + String(analogRead(A5)));
      digitalWrite(PIN_TRIG, LOW);
      delayMicroseconds(5);
      digitalWrite(PIN_TRIG, HIGH);
      delayMicroseconds(10);
      digitalWrite(PIN_TRIG, LOW);
      duration = pulseIn(PIN_ECHO, HIGH);
      cm = (duration/2)/29.1;
      Serial.println("Distance: " + String(cm) + "cm");
      unsigned long currentMillis = millis();
      if (currentMillis - previousMillis > LOG_PERIOD){
        previousMillis = currentMillis;
        Serial.print("Radiation: " + String(counts));
        counts = 0;
      }
      Serial.println("");
      Serial.println("********");
      Serial.println("");
      delay(500);
    }
    else if (20>LX>-20 && 20>LY>-20){
      digitalWrite(26,LOW);
      digitalWrite(28,LOW);
    }
    if (s3>0){
      digitalWrite(24, HIGH);
    }
    else{
      digitalWrite(24, LOW);
    }
  }

}
