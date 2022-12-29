/*
  ReadTemperatures
*/

void setup() {
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
}

float t_min0 = 0.0;
float t_max0 = 40.0;
float v_max0 = 10.0;

float t_min1 = 0.0;
float t_max1 = 40.0;
float v_max1 = 10.0;

float t_delta0 = t_max0 - t_min0;
float t_delta1 = t_max1 - t_min1;

void loop() {
  int a0 = analogRead(A0);
  int a1 = analogRead(A1);

  float v0 = a0 * (5.0 / 1023.0);
  float v1 = a1 * (5.0 / 1023.0);

  float t0 = t_min0 + (v0 / v_max0) * t_delta0;
  float t1 = t_min0 + (v0 / v_max0) * t_delta1;
  

  Serial.print(a0);
  Serial.print(", ");
  Serial.print(v0);
  Serial.print(" V, ");
  Serial.print(t0);
  Serial.print(" C, ");
  Serial.print(a1);
  Serial.print(", ");
  Serial.print(v1);
  Serial.print(" V, ");
  Serial.print(t1);
  Serial.print(" C\n");
  delay(1000);
}
