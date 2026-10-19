// ESP32-C3 Modern Signal Tower
int bulbs[] = {0, 1, 2, 3}; // 0 පහලම, 3 උඩම
int bulbCount = 4;

void setup() {
  for (int i = 0; i < bulbCount; i++) {
    pinMode(bulbs[i], OUTPUT);
  }
}

// Bulb එකක Brightness එක හදන Function එක
void setBrightness(int pin, int brightness) {
  analogWrite(pin, brightness); // ESP32-C3 වල PWM වලින් Fade වෙනවා
}

void loop() {

//  // 1. EFFECT 1: POWER BUILD-UP - පහල ඉඳන් උඩට Tower එක Fill වෙනවා
//  for (int i = 0; i < bulbCount; i++) {
//    for (int b = 0; b <= 255; b += 5) { // පහල ඉඳන් Bright වෙනවා
//      setBrightness(bulbs[i], b);
//      delay(5);
//    }
//    setBrightness(bulbs[i], 255); // ඒ Bulb එක ON එකේම තියෙනවා
//    delay(100);
//  }
//  delay(800);
//
//  // 2. EFFECT 2: MODERN BEACON PULSE - 4ම එකට Double Pulse වෙනවා (Real Tower වගේ)
//  for(int k=0; k<2; k++){
//    for (int b = 0; b <= 255; b += 10) {
//      for(int i=0; i<bulbCount; i++) setBrightness(bulbs[i], b);
//      delay(5);
//    }
//    for (int b = 255; b >= 0; b -= 15) {
//      for(int i=0; i<bulbCount; i++) setBrightness(bulbs[i], b);
//      delay(5);
//    }
//    delay(150);
//  }
//  delay(1000);
//
//  // 3. EFFECT 3: METEOR FALL - උඩ ඉඳන් පහලට දිය ඇල්ලක් වගේ වැටෙනවා
//  for (int i = bulbCount - 1; i >= 0; i--) {
//    // උඩ එක Full Bright
//    setBrightness(bulbs[i], 255);
//    // යට තියෙන එක 50% Bright (Tail එක)
//    if (i > 0) setBrightness(bulbs[i-1], 80);
//    if (i > 1) setBrightness(bulbs[i-2], 10);
//
//    delay(120);
//
//    // ඔක්කොම Off
//    for(int j=0; j<bulbCount; j++) setBrightness(bulbs[j], 0);
//  }
//  delay(300);

  // 4. EFFECT 4: KNIGHT RIDER SCAN - පහල ඉඳන් උඩට, උඩ ඉඳන් පහලට Scanner එකක් යනවා
  for(int rep=0; rep<2; rep++){
    for (int i = 0; i < bulbCount; i++) {
      setBrightness(bulbs[i], 255);
      delay(80);
      setBrightness(bulbs[i], 0);
    }
    for (int i = bulbCount - 2; i > 0; i--) {
      setBrightness(bulbs[i], 255);
      delay(80);
      setBrightness(bulbs[i], 0);
    }
  }
  delay(1000);
}
