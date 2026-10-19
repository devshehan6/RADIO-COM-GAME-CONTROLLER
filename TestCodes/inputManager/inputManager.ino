
void setup() {
  Serial.begin(115200);
  Serial.println("text");
  
  pinMode(21, INPUT);
  pinMode(20, INPUT);
  pinMode(10, INPUT);
  pinMode(9, INPUT);

  
}

void loop() {
  int a = digitalRead(21);
  int b = digitalRead(20);
  int c = digitalRead(10);
  int d = digitalRead(9);


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
