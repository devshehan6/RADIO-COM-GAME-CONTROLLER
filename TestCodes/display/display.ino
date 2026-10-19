#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

// ඔයා දීලා තියෙන Pins
#define SDA_PIN 8
#define SCL_PIN 7

#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup() {
  Serial.begin(115200);
  delay(1000);

  // C3 එකේ SDA, SCL Pins මාරු කරන තැන - මේක තමයි වැදගත්ම
  Wire.begin(SDA_PIN, SCL_PIN);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { 
    Serial.println("SSD1306 allocation failed");
    for(;;);
  }
  
  display.clearDisplay();
  Serial.println("OLED Ready");
}

void loop() {
  // සුපිරි Modern Signal Tower Animation එක
  display.clearDisplay();

  // Tower එකේ කනුව
  display.drawLine(64, 10, 64, 60, SSD1306_WHITE);
  display.drawLine(50, 60, 78, 60, SSD1306_WHITE);

  // පහල ඉඳන් උඩට බල්බ් 4
  // 0 - පහලම
  display.fillCircle(64, 55, 4, SSD1306_WHITE);
  // 1
  display.drawCircle(64, 43, 4, SSD1306_WHITE);
  // 2
  display.drawCircle(64, 31, 4, SSD1306_WHITE);
  // 3 - උඩම
  display.drawCircle(64, 19, 4, SSD1306_WHITE);

  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.print("TOWER: OK");

  display.display();
  delay(300);

  // දැන් උඩට යන Animation එක
  for(int i=0; i<4; i++){
    display.clearDisplay();
    display.setCursor(0,0);
    display.print("TOWER: SCAN");
    display.drawLine(64, 10, 64, 60, SSD1306_WHITE);
    display.drawLine(50, 60, 78, 60, SSD1306_WHITE);

    int yPos[] = {55, 43, 31, 19};
    for(int j=0; j<4; j++){
      if(j==i) display.fillCircle(64, yPos[j], 5, SSD1306_WHITE);
      else display.drawCircle(64, yPos[j], 4, SSD1306_WHITE);
    }
    display.display();
    delay(120);
  }
}