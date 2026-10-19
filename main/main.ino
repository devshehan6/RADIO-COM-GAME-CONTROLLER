#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define SDA_PIN 8
#define SCL_PIN 7
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Bulbs
int bulbs[] = {0, 1, 2, 3};
int bulbCount = 4;

// Inputs - A=21, B=20, C=10, D=9
int pinA = 21, pinB = 20, pinC = 10, pinD = 9;

void setBrightness(int pin, int b){ analogWrite(pin, b); }

// Timing - Delay නැතිව
unsigned long lastBulbTrigger = 0;
unsigned long lastBulbStep = 0;
unsigned long lastDisplay = 0;
unsigned long lastSerial = 0;
unsigned long bootTime = 0;

int displayState = 0; // 0=WELCOME, 1=NAME, 2=TIME
bool bulbEffectActive = false;
int rep = 0;
int bulbIndex = 0;
int phase = 0; // 0=up, 1=down

// Input Ball Draw Function
void drawInputBalls(int a, int b, int c, int d){
  // පහලින් බෝල 4 - A B C D
  int y = 55;
  int xPos[] = {20, 50, 80, 110};
  int vals[] = {a, b, c, d};
  char labels[] = {'A','B','C','D'};

  for(int i=0; i<4; i++){
    if(vals[i]==1) display.fillCircle(xPos[i], y, 5, SSD1306_WHITE);
    else display.drawCircle(xPos[i], y, 5, SSD1306_WHITE);
    
    display.setCursor(xPos[i]-2, y+8);
    display.print(labels[i]);
  }
}

void setup(){
  Serial.begin(115200);
  delay(1000);
  Wire.begin(SDA_PIN, SCL_PIN);
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.setTextColor(SSD1306_WHITE);
  
  for(int i=0;i<4;i++){ pinMode(bulbs[i], OUTPUT); setBrightness(bulbs[i],0); }
  pinMode(pinA, INPUT_PULLDOWN); pinMode(pinB, INPUT_PULLDOWN);
  pinMode(pinC, INPUT_PULLDOWN); pinMode(pinD, INPUT_PULLDOWN);
  
  bootTime = millis();
}

void loop(){
  unsigned long now = millis();

  if(now - lastSerial >= 50){ 
    lastSerial = now;
    int a = digitalRead(pinA);
    int b = digitalRead(pinB);
    int c = digitalRead(pinC);
    int d = digitalRead(pinD);
    Serial.print(b); Serial.print(c); Serial.print(a); Serial.println(d);
  }

  if(!bulbEffectActive && now - lastBulbTrigger >= 4000){
    bulbEffectActive = true;
    lastBulbTrigger = now;
    rep = 0; bulbIndex = 0; phase = 0;
    for(int i=0;i<4;i++) setBrightness(bulbs[i],0);
  }

  if(bulbEffectActive && now - lastBulbStep >= 80){
    lastBulbStep = now;
    
    for(int i=0;i<4;i++) setBrightness(bulbs[i],0);

    if(phase==0){ 
      setBrightness(bulbs[bulbIndex], 255);
      bulbIndex++;
      if(bulbIndex >= bulbCount){
        bulbIndex = bulbCount - 2;
        phase = 1;
      }
    } else {
      setBrightness(bulbs[bulbIndex], 255);
      bulbIndex--;
      if(bulbIndex <= 0){
        bulbIndex = 0;
        phase = 0;
        rep++;
        if(rep >= 2){
          bulbEffectActive = false;
          for(int i=0;i<4;i++) setBrightness(bulbs[i],0);
        }
      }
    }
  }

  // 3. DISPLAY
  if(now - lastDisplay >= 1500){
    lastDisplay = now;
    int a = digitalRead(pinA); int b = digitalRead(pinB);
    int c = digitalRead(pinC); int d = digitalRead(pinD);

    display.clearDisplay();

    if(displayState==0){
      display.setTextSize(2); display.setCursor(15,20); display.println("WELCOME");
      displayState=1;
    } else if(displayState==1){
      display.setTextSize(1); display.setCursor(10,10); display.println("DEV SHEHAN's");
      display.setTextSize(2); display.setCursor(20,30); display.println("TOWER");
      displayState=2;
    } else {
      unsigned long totalSec = (now - bootTime) / 1000;
      int h = (totalSec / 3600) % 24;
      int m = (totalSec / 60) % 60;
      int s = totalSec % 60;

      display.setTextSize(1); display.setCursor(30,0); display.println("TIME");
      display.setTextSize(2); display.setCursor(15,20);
      if(h<10) display.print("0"); display.print(h); display.print(":");
      if(m<10) display.print("0"); display.print(m); display.print(":");
      if(s<10) display.print("0"); display.print(s);
    }
    
    drawInputBalls(a,b,c,d);
    
    display.display();
  }
}