#include <Servo.h>

Servo servoX;
Servo servoY;

int servoXAngle = 90;  // Initial angle for servo X
int servoYAngle = 90;  // Initial angle for servo Y

void setup() {
  servoX.attach(10);    // Attach servo X to digital pin 9
  servoY.attach(9);   // Attach servo Y to digital pin 10
  Serial.begin(9600);  // Initialize serial communication
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    int commaIndex = data.indexOf(',');

    if (data.startsWith("2:") && commaIndex > 0) {
      int posX = data.substring(2, commaIndex).toInt();
      int posY = data.substring(commaIndex + 1).toInt();

      // Map and constrain the positions to servo angles
      servoXAngle = map(posX, 0, 640, 0, 180);  // Adjust as needed
      servoYAngle = map(posY, 0, 240, 0, 180);  // Adjust as needed

      // Set the servo angles
      servoX.write(constrain(servoXAngle, 0, 180));
      servoY.write(constrain(servoYAngle, 0, 180));
    }
  }
}
