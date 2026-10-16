#include <Arduino.h>
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_GC9A01A.h>
#include <math.h>
#include <ctype.h>

// Hardware-verified GPIOs: shared SPI + DC, independent CS + RST.
constexpr int PIN_SCK=12, PIN_MOSI=11, PIN_DC=10;
constexpr int PIN_CS_0=13, PIN_CS_1=14;
constexpr int PIN_RST_0=9, PIN_RST_1=8;

Adafruit_GC9A01A lcd0(PIN_CS_0, PIN_DC, PIN_RST_0);
Adafruit_GC9A01A lcd1(PIN_CS_1, PIN_DC, PIN_RST_1);

struct Amp { float re; float im; };
Amp alpha={1.0f,0.0f}, beta={0.0f,0.0f};
constexpr float INV_SQRT2=0.70710678118f;
constexpr float PI_F=3.14159265359f;
constexpr float QUBIT_EPSILON=0.00001f;

float probability(const Amp &a) { return a.re*a.re+a.im*a.im; }
Amp negate(const Amp &a) { return {-a.re,-a.im}; }
Amp plus(const Amp &a,const Amp &b) { return {a.re+b.re,a.im+b.im}; }
Amp minusAmp(const Amp &a,const Amp &b) { return {a.re-b.re,a.im-b.im}; }
Amp timesI(const Amp &a) { return {-a.im,a.re}; }
Amp timesMinusI(const Amp &a) { return {a.im,-a.re}; }

void normalizeState() {
  float norm=sqrtf(probability(alpha)+probability(beta));
  if (norm<QUBIT_EPSILON) { alpha={1.0f,0.0f}; beta={0.0f,0.0f}; return; }
  alpha.re/=norm; alpha.im/=norm;
  beta.re/=norm; beta.im/=norm;
}

// Gauge: alpha phase is zero whenever both amplitudes are nonzero.
// No phase hand is drawn for a zero-probability amplitude.
float phaseFor(int which) {
  float p0=probability(alpha),p1=probability(beta);
  if (which==0 || p0<QUBIT_EPSILON || p1<QUBIT_EPSILON) return 0.0f;
  return atan2f(beta.im,beta.re)-atan2f(alpha.im,alpha.re);
}

// Warm orange contrasts with the cyan fill; black label panel retains
// contrast regardless of probability. Colors are RGB565.
constexpr uint16_t COLOR_HAND = 0xFD20;
constexpr uint16_t COLOR_LABEL_BG = GC9A01A_BLACK;

void drawThickHand(Adafruit_GC9A01A &lcd, int cx, int cy,
                   float angle, int length) {
  const int halfWidth = 4;
  float px = -sinf(angle), py = cosf(angle);
  int x1 = cx + (int)lroundf(px * halfWidth);
  int y1 = cy + (int)lroundf(py * halfWidth);
  int x2 = cx - (int)lroundf(px * halfWidth);
  int y2 = cy - (int)lroundf(py * halfWidth);
  int ex = cx + (int)lroundf(length * cosf(angle));
  int ey = cy + (int)lroundf(length * sinf(angle));
  lcd.fillTriangle(x1, y1, x2, y2, ex, ey, COLOR_HAND);
  lcd.fillCircle(cx, cy, 4, GC9A01A_WHITE);
  lcd.fillCircle(ex, ey, 2, COLOR_HAND);
}

void drawStateLabel(Adafruit_GC9A01A &lcd, int which) {
  // Redraw last so it remains readable atop a fully filled probability disk.
  const int x = 93, y = 195, w = 54, h = 28;
  lcd.fillRoundRect(x, y, w, h, 6, COLOR_LABEL_BG);
  lcd.drawRoundRect(x, y, w, h, 6, GC9A01A_WHITE);
  lcd.setTextSize(2);
  lcd.setTextColor(GC9A01A_WHITE, COLOR_LABEL_BG);
  lcd.setCursor(x + 3, y + 6);
  lcd.print(which == 0 ? "|0>" : "|1>");
}

void drawAmplitude(Adafruit_GC9A01A &lcd,int which) {
  float p=fminf(1.0f,fmaxf(0.0f,which==0?probability(alpha):probability(beta)));
  const int cx=120,cy=120,outerR=106;
  lcd.fillScreen(GC9A01A_BLACK);
  lcd.drawCircle(cx,cy,110,GC9A01A_WHITE);
  int radius=(int)lroundf(outerR*sqrtf(p)); // area proportional to probability
  if (radius>0) {
    lcd.fillCircle(cx,cy,radius,GC9A01A_CYAN);
    float angle=phaseFor(which)-PI_F/2.0f;
    int handR=radius>9?radius-5:radius;
    drawThickHand(lcd,cx,cy,angle,handR);
  }
  drawStateLabel(lcd,which);
}

void showState() {
  digitalWrite(PIN_CS_1,HIGH);
  drawAmplitude(lcd0,0);
  digitalWrite(PIN_CS_0,HIGH);
  drawAmplitude(lcd1,1);
  float p0=probability(alpha),p1=probability(beta);
  Serial.printf("P(0)=%.1f%% P(1)=%.1f%%",p0*100,p1*100);
  if (p0>QUBIT_EPSILON && p1>QUBIT_EPSILON) {
    float deg=phaseFor(1)*180.0f/PI_F;
    while(deg<0) deg+=360.0f;
    while(deg>=360) deg-=360.0f;
    Serial.printf(" relative phase=%.1f deg",deg);
  } else {
    Serial.print(" relative phase=undefined (one amplitude zero)");
  }
  Serial.println();
}

void applyCommand(char cmd) {
  Amp a=alpha,b=beta;
  switch(cmd) {
    case 'X': alpha=b;beta=a;break;
    case 'Y': alpha=timesMinusI(b);beta=timesI(a);break;
    case 'Z': beta=negate(b);break;
    case 'H':
      alpha=plus(a,b);beta=minusAmp(a,b);
      alpha.re*=INV_SQRT2;alpha.im*=INV_SQRT2;
      beta.re*=INV_SQRT2;beta.im*=INV_SQRT2;
      break;
    case 'R': alpha={1,0};beta={0,0};break;
    case 'M': {
      float p0=probability(alpha);
      float draw=(float)random(1000000)/1000000.0f;
      bool zero=draw<p0;
      alpha=zero?Amp{1,0}:Amp{0,0};
      beta=zero?Amp{0,0}:Amp{1,0};
      Serial.printf("Measurement result: %d\n",zero?0:1);
      break;
    }
    default:
      Serial.println("Commands: X Y Z H M (measure) R (reset)");
      return;
  }
  normalizeState();
  Serial.printf("Applied %c. ",cmd);
  showState();
}

void setup() {
  Serial.begin(115200);
  delay(1200);
  randomSeed((uint32_t)micros());
  pinMode(PIN_CS_0,OUTPUT);
  pinMode(PIN_CS_1,OUTPUT);
  digitalWrite(PIN_CS_0,HIGH);
  digitalWrite(PIN_CS_1,HIGH);
  SPI.begin(PIN_SCK,-1,PIN_MOSI,PIN_CS_0);
  lcd0.begin(10000000);
  lcd1.begin(10000000);
  Serial.println("My First Qubit - serial controller");
  Serial.println("Type X, Y, Z, H, M, or R and press Send.");
  showState();
}

void loop() {
  while(Serial.available()) {
    char c=(char)Serial.read();
    if(c=='\n'||c=='\r'||c==' '||c=='\t') continue;
    applyCommand((char)toupper((unsigned char)c));
  }
}
