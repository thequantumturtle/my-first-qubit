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

// V0.2 display: cheerful coral orange (#FF783C, RGB565) and a
// constant-width phase hand. One offscreen framebuffer avoids the
// black-screen wipes caused by drawing directly to the LCD.
constexpr uint16_t COLOR_HAND = 0xFBC7;
constexpr uint16_t COLOR_LABEL_BG = GC9A01A_BLACK;
constexpr int SCREEN_SIZE = 240;
constexpr int ANIMATION_STEPS = 8;
GFXcanvas16 frame(SCREEN_SIZE, SCREEN_SIZE); // 115200 bytes; ESP32-S3 N8R8

float shownP0 = 1.0f;
float shownPhase = 0.0f;
bool hasShownFrame = false;

float smoothStep(float t) { return t*t*(3.0f-2.0f*t); }
float shortestAngle(float from, float to) {
  float diff = remainderf(to-from, 2.0f*PI_F);
  return diff;
}

void drawHand(GFXcanvas16 &canvas, int cx, int cy,
              float angle, int length) {
  const int halfWidth = 3;
  float dx=cosf(angle),dy=sinf(angle);
  float px=-dy,py=dx;
  int ax=cx+(int)lroundf(px*halfWidth);
  int ay=cy+(int)lroundf(py*halfWidth);
  int bx=cx-(int)lroundf(px*halfWidth);
  int by=cy-(int)lroundf(py*halfWidth);
  int ex=cx+(int)lroundf(dx*length);
  int ey=cy+(int)lroundf(dy*length);
  int cx2=ex+(int)lroundf(px*halfWidth);
  int cy2=ey+(int)lroundf(py*halfWidth);
  int dx2=ex-(int)lroundf(px*halfWidth);
  int dy2=ey-(int)lroundf(py*halfWidth);
  // Two triangles form a constant-width rectangle.
  canvas.fillTriangle(ax,ay,bx,by,cx2,cy2,COLOR_HAND);
  canvas.fillTriangle(bx,by,cx2,cy2,dx2,dy2,COLOR_HAND);
  canvas.fillCircle(cx,cy,4,GC9A01A_WHITE);
  canvas.fillCircle(ex,ey,halfWidth,COLOR_HAND);
}

void drawLabel(GFXcanvas16 &canvas,int which) {
  const int x=93,y=195,w=54,h=28;
  canvas.fillRoundRect(x,y,w,h,6,COLOR_LABEL_BG);
  canvas.drawRoundRect(x,y,w,h,6,GC9A01A_WHITE);
  canvas.setTextSize(2);
  canvas.setTextColor(GC9A01A_WHITE,COLOR_LABEL_BG);
  canvas.setCursor(x+3,y+6);
  canvas.print(which==0?"|0>":"|1>");
}

void renderDisplay(Adafruit_GC9A01A &lcd,int which,
                   float p,float relativePhase) {
  const int cx=120,cy=120,outerR=106;
  frame.fillScreen(GC9A01A_BLACK);
  frame.drawCircle(cx,cy,110,GC9A01A_WHITE);
  int radius=(int)lroundf(outerR*sqrtf(fminf(1.0f,fmaxf(0.0f,p))));
  if(radius>0) {
    frame.fillCircle(cx,cy,radius,GC9A01A_CYAN);
    // Zero phase always points up; |1> shows the relative phase.
    float angle=(which==0?0.0f:relativePhase)-PI_F/2.0f;
    int length=radius>9?radius-5:radius;
    drawHand(frame,cx,cy,angle,length);
  }
  drawLabel(frame,which);
  lcd.drawRGBBitmap(0,0,frame.getBuffer(),SCREEN_SIZE,SCREEN_SIZE);
}

void showState() {
  float p0=probability(alpha),p1=probability(beta);
  float newPhase=phaseFor(1);
  bool phaseDefined=p0>QUBIT_EPSILON && p1>QUBIT_EPSILON;
  // Preserve the last meaningful phase when an amplitude vanishes.
  float destinationPhase=phaseDefined?newPhase:shownPhase;
  if(!frame.getBuffer()) {
    Serial.println("ERROR: Display framebuffer allocation failed");
    return;
  }

  int steps=hasShownFrame?ANIMATION_STEPS:1;
  for(int i=1;i<=steps;i++) {
    float t=smoothStep((float)i/(float)steps);
    float intermediateP0=shownP0+(p0-shownP0)*t;
    float intermediatePhase=shownPhase+
      shortestAngle(shownPhase,destinationPhase)*t;
    digitalWrite(PIN_CS_1,HIGH);
    renderDisplay(lcd0,0,intermediateP0,0.0f);
    digitalWrite(PIN_CS_0,HIGH);
    renderDisplay(lcd1,1,1.0f-intermediateP0,intermediatePhase);
  }
  shownP0=p0;
  shownPhase=destinationPhase;
  hasShownFrame=true;

  Serial.printf("P(0)=%.1f%% P(1)=%.1f%%",p0*100,p1*100);
  if(phaseDefined) {
    float deg=newPhase*180.0f/PI_F;
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
