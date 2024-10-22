//Arduino motor code to base the python off of
#include <SoftwareSerial.h>

const byte FULL_FORWARD_M1 = 127;
const byte FULL_FORWARD_M2 = 255;
const byte STOP_M1 = 64;
const byte STOP_M2 = 192;
const byte REVERSE_M1 = 1;
const byte REVERSE_M2 = 128;

//pin 10 (RX) and 11 (TX)
SoftwareSerial mySerial(10, 11); // RX, TX

void setup() {
  Serial.begin(38400);
  mySerial.begin(38400);
}

void loop() {
  //full forward


  Serial.println("Motor 1 forward");
  mySerial.write(FULL_FORWARD_M1);
  Serial.println("Motor 2 forward");
  mySerial.write(FULL_FORWARD_M2);

  // Serial.println("Delay");
  // delay(1000);



  Serial.println("Delay 2 seconds");
  delay(2000);

  //should be complete stop
  Serial.println("Motor 1 stop");
  mySerial.write(STOP_M1);

  // Serial.println("Delay");
  // delay(1000);

  Serial.println("Motor 2 stop");
  mySerial.write(STOP_M2);

  Serial.println("Delay 2 seconds");
  delay(2000);

  //work in progress: reverse
  Serial.println("Motor 1 reverse");
  mySerial.write(REVERSE_M1);

  // Serial.println("Delay");
  // delay(1000);

  Serial.println("Motor 2 reverse");
  mySerial.write(REVERSE_M2);

  Serial.println("End of loop; delay 5 seconds");
  delay(5000);
}