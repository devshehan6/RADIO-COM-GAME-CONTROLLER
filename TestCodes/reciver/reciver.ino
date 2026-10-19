void setup() {
  Serial.begin(115200);
  
  pinMode(34, INPUT);
  pinMode(35, INPUT);
  pinMode(32, INPUT);
  pinMode(33, INPUT);

  
}

void loop() {
  int a = digitalRead(34);
  int b = digitalRead(35);
  int c = digitalRead(32);
  int d = digitalRead(33);


  Serial.print(b);
  Serial.print("");
  Serial.print(c);
  Serial.print("");
  Serial.print(a);
  Serial.print("");
  Serial.print(d);
  Serial.println("");
  delay(100);
  
}