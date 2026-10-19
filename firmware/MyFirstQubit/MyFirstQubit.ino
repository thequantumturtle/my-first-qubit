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
// Normally-open buttons: each assigned GPIO to GND, internal pull-ups.
// Keep H on its hardware-verified GPIO 4; new inputs avoid display pins.
constexpr uint32_t BUTTON_DEBOUNCE_MS=30;
struct Button {
  int pin;
  char command;
  bool raw,stable;
  uint32_t changedAt;
};
Button buttons[] = {
  {4,'H',HIGH,HIGH,0},
  {5,'X',HIGH,HIGH,0},
  {6,'Y',HIGH,HIGH,0},
  {7,'Z',HIGH,HIGH,0},
  {15,'M',HIGH,HIGH,0},
  {16,'R',HIGH,HIGH,0},
  {17,'C',HIGH,HIGH,0}
};

// PEC11R-4225F-S0024: 24 pulses and detents/revolution, four edges/click.
struct Encoder {
  int pinA,pinB;
  volatile uint8_t previous;
  volatile int quarters;
  volatile int32_t pending;
  uint8_t rest;
};
Encoder probabilityEncoder={1,2,0,0,0,0};
Encoder phaseEncoder={41,42,0,0,0,0};
portMUX_TYPE encoderMux=portMUX_INITIALIZER_UNLOCKED;

Adafruit_GC9A01A lcd0(PIN_CS_0, PIN_DC, PIN_RST_0);
Adafruit_GC9A01A lcd1(PIN_CS_1, PIN_DC, PIN_RST_1);

struct Amp { float re; float im; };
Amp alpha={1.0f,0.0f}, beta={0.0f,0.0f};
constexpr float INV_SQRT2=0.70710678118f;
constexpr float PI_F=3.14159265359f;
constexpr float QUBIT_EPSILON=1e-10f;
float relativePhaseMemory=0.0f;
constexpr float PROBABILITY_STEP=5.0f*PI_F/180.0f; // theta, like browser balance
constexpr float PHASE_STEP=15.0f*PI_F/180.0f;

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

// Each hand shows its complex amplitude's phase, as in the simulator.
// Phase is undefined for a zero amplitude; renderDisplay hides its hand.
float phaseFor(int which) {
  const Amp &a = which == 0 ? alpha : beta;
  return probability(a)>QUBIT_EPSILON ? atan2f(a.im,a.re) : 0.0f;
}

// Display-only palettes. A palette change never changes the amplitudes.
struct Palette {
  const char *name;
  uint16_t background,empty,outline,zero,one,hand;
};
constexpr uint16_t rgb565(uint32_t rgb) {
  return ((rgb>>8)&0xF800)|((rgb>>5)&0x07E0)|((rgb>>3)&0x001F);
}
constexpr Palette PALETTES[] = {
  {"Woodland",rgb565(0xFCF6E8),rgb565(0xE2D6BE),rgb565(0x927B5B),
              rgb565(0x5D9ED0),rgb565(0xE99B66),rgb565(0x443726)},
  {"Garden",  rgb565(0xF7F3E8),rgb565(0xDEDCCB),rgb565(0x7C846B),
              rgb565(0x82A878),rgb565(0xCE9494),rgb565(0x303D2F)},
  {"Night",   rgb565(0x172638),rgb565(0x2B3D50),rgb565(0x8998A5),
              rgb565(0x80B9D8),rgb565(0xD9B56D),rgb565(0x172638)}
};
constexpr unsigned PALETTE_COUNT=sizeof(PALETTES)/sizeof(PALETTES[0]);
unsigned paletteIndex=0;
const Palette &palette(); // Explicit prototype after Palette for Arduino preprocessing.
const Palette &palette() { return PALETTES[paletteIndex]; }
constexpr int SCREEN_SIZE = 240;
// Faster SPI and shorter transitions reduce full-frame transfer time.
// For unstable breadboard wiring, lower SPI_HZ to 20000000.
constexpr uint32_t SPI_HZ = 40000000;
// Browser reference: 720 ms gates, 460 ms measurement/reset.
GFXcanvas16 frame(SCREEN_SIZE, SCREEN_SIZE); // 115200 bytes; ESP32-S3 N8R8

float shownP0 = 1.0f;
float shownPhase0 = 0.0f, shownPhase1 = 0.0f;
bool hasShownFrame = false;

float shortestAngle(float from, float to) {
  float diff = remainderf(to-from, 2.0f*PI_F);
  return diff;
}

// Count a complete cycle only on return to the physical detent sampled at
// startup. Anchor clicks at rest so bounce cannot leave reversal dead travel.
// No drawing, floats or serial in this ISR.
void ARDUINO_ISR_ATTR encoderChanged(void *arg) {
  Encoder *encoder=static_cast<Encoder *>(arg);
  uint8_t next=(digitalRead(encoder->pinA)<<1)|digitalRead(encoder->pinB);
  portENTER_CRITICAL_ISR(&encoderMux);
  uint8_t previous=encoder->previous;
  uint8_t transition=(previous<<2)|next;
  if((previous^next)==3) encoder->quarters=0; // Missed/invalid transition.
  else {
    int delta=0;
    switch(transition) {
      case 2: case 4: case 11: case 13: delta=1;break;
      case 1: case 7: case 8: case 14: delta=-1;break;
    }
    encoder->quarters+=delta;
    if(next==encoder->rest) {
      if(encoder->quarters==4) encoder->pending++;
      else if(encoder->quarters==-4) encoder->pending--;
      encoder->quarters=0;
    }
  }
  encoder->previous=next;
  portEXIT_CRITICAL_ISR(&encoderMux);
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
  canvas.fillTriangle(ax,ay,bx,by,cx2,cy2,palette().hand);
  canvas.fillTriangle(bx,by,cx2,cy2,dx2,dy2,palette().hand);
  canvas.fillCircle(cx,cy,4,palette().hand);
  canvas.fillCircle(ex,ey,halfWidth,palette().hand);
}

void drawLabel(GFXcanvas16 &canvas,int which) {
  const int x=93,y=195,w=54,h=28;
  canvas.fillRoundRect(x,y,w,h,6,palette().background);
  canvas.drawRoundRect(x,y,w,h,6,palette().outline);
  canvas.setTextSize(2);
  canvas.setTextColor(paletteIndex==2?palette().outline:palette().hand,palette().background);
  canvas.setCursor(x+3,y+6);
  canvas.print(which==0?"|0>":"|1>");
}

void renderDisplay(Adafruit_GC9A01A &lcd,int which,
                   float p,float amplitudePhase) {
  const int cx=120,cy=120,outerR=106;
  frame.fillScreen(palette().background);
  frame.fillCircle(cx,cy,outerR,palette().empty);
  frame.drawCircle(cx,cy,110,palette().outline);
  int radius=(int)lroundf(outerR*sqrtf(fminf(1.0f,fmaxf(0.0f,p))));
  if(radius>0) {
    frame.fillCircle(cx,cy,radius,which==0?palette().zero:palette().one);
    // Positive phase turns clockwise from up, matching the browser.
    float angle=amplitudePhase-PI_F/2.0f;
    int length=radius>9?radius-5:radius;
    if(p>QUBIT_EPSILON) drawHand(frame,cx,cy,angle,length);
  }
  drawLabel(frame,which);
  lcd.drawRGBBitmap(0,0,frame.getBuffer(),SCREEN_SIZE,SCREEN_SIZE);
}

void showState(bool report=true) {
  float p0=probability(alpha),p1=probability(beta);
  float phase0=phaseFor(0),phase1=phaseFor(1);
  float newPhase=phase1-phase0;
  bool phaseDefined=p0>QUBIT_EPSILON && p1>QUBIT_EPSILON;
  if(phaseDefined) relativePhaseMemory=remainderf(newPhase,2.0f*PI_F);
  if(!frame.getBuffer()) {
    Serial.println("ERROR: Display framebuffer allocation failed");
    return;
  }
  bool visiblyChanged = !hasShownFrame ||
      fabsf(p0-shownP0)>0.0001f ||
      (p0>QUBIT_EPSILON && fabsf(shortestAngle(shownPhase0,phase0))>0.0001f) ||
      (p1>QUBIT_EPSILON && fabsf(shortestAngle(shownPhase1,phase1))>0.0001f);
  if(visiblyChanged) {
    unsigned long drawStart=millis();
    digitalWrite(PIN_CS_1,HIGH);
    renderDisplay(lcd0,0,p0,phase0);
    digitalWrite(PIN_CS_0,HIGH);
    renderDisplay(lcd1,1,p1,phase1);
    if(report) Serial.printf("Display update: %lu ms (1 frame pair)\n",millis()-drawStart);
  }
  shownP0=p0;
  shownPhase0=phase0;
  shownPhase1=phase1;
  hasShownFrame=true;

  if(!report) return;
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

Amp scaled(const Amp &a,float k) { return {a.re*k,a.im*k}; }
Amp multiply(const Amp &a,const Amp &b) {
  return {a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re};
}
void gateResult(char cmd,const Amp &a,const Amp &b,Amp &outA,Amp &outB) {
  switch(cmd) {
    case 'X': outA=b;outB=a;break;
    case 'Y': outA=timesMinusI(b);outB=timesI(a);break;
    case 'Z': outA=a;outB=negate(b);break;
    default: outA=scaled(plus(a,b),INV_SQRT2);
             outB=scaled(minusAmp(a,b),INV_SQRT2);break;
  }
}
// Same path as browser gateState:
// exp(i*t/2) [cos(t/2) I - i*sin(t/2) G], t from 0 to pi.
Amp gateSample(const Amp &initial,const Amp &transformed,float fraction) {
  float half=PI_F*fraction/2.0f;
  Amp factor={cosf(half),sinf(half)};
  return multiply(factor,plus(scaled(initial,cosf(half)),
                  timesMinusI(scaled(transformed,sinf(half)))));
}
void animateState(const Amp &a,const Amp &b,const Amp &targetA,
                  const Amp &targetB,bool unitary,uint32_t duration) {
  uint32_t start=millis();
  int frames=0;
  while(true) {
    float fraction=fminf(1.0f,(float)(millis()-start)/(float)duration);
    float eased=fraction*fraction*(3.0f-2.0f*fraction);
    // Snap exactly to the gate result to avoid trigonometric residue.
    if(fraction>=1.0f) { alpha=targetA;beta=targetB; }
    else if(unitary) {
      alpha=gateSample(a,targetA,eased);
      beta=gateSample(b,targetB,eased);
    } else {
      // Measurement/reset: normalized visual interpolation, not a gate.
      alpha=plus(scaled(a,1-eased),scaled(targetA,eased));
      beta=plus(scaled(b,1-eased),scaled(targetB,eased));
    }
    normalizeState();
    showState(false);
    frames++;
    if(fraction>=1.0f) break;
    delay(1); // Yield even when consecutive frames are visually identical.
  }
  Serial.printf("Animation: %lu ms (%d samples)\n",millis()-start,frames);
}
void applyCommand(char cmd) {
  if(cmd=='C') {
    paletteIndex=(paletteIndex+1)%PALETTE_COUNT;
    hasShownFrame=false; // Force both LCDs to repaint, even at the same state.
    Serial.printf("Palette: %s\n",palette().name);
    showState();
    return;
  }
  Amp a=alpha,b=beta,targetA=a,targetB=b;
  bool unitary=cmd=='X'||cmd=='Y'||cmd=='Z'||cmd=='H';
  if(unitary) gateResult(cmd,a,b,targetA,targetB);
  else if(cmd=='R') { targetA={1,0};targetB={0,0}; }
  else if(cmd=='M') {
    float draw=(float)random(1000000)/1000000.0f;
    bool zero=draw<probability(a);
    Amp selected=zero?a:b;
    float magnitude=sqrtf(probability(selected));
    Amp collapsed=scaled(selected,1.0f/magnitude);
    targetA=zero?collapsed:Amp{0,0};
    targetB=zero?Amp{0,0}:collapsed;
    Serial.printf("Measurement result: %d\n",zero?0:1);
  } else {
    Serial.println("Commands: X Y Z H M (measure) R (reset) C (colors)");
    return;
  }
  animateState(a,b,targetA,targetB,unitary,unitary?720:460);
  if(cmd=='R') relativePhaseMemory=0.0f;
  Serial.printf("Applied %c. ",cmd);
  showState();
}

// Same state construction as browser setAngles: keep the current reference
// phase, set theta and relative phase; retain phi at either probability pole.
void setKnobAngles(float theta,float phi) {
  float global=probability(alpha)>QUBIT_EPSILON?atan2f(alpha.im,alpha.re):
               atan2f(beta.im,beta.re)-relativePhaseMemory;
  Amp reference={cosf(global),sinf(global)};
  Amp offset={cosf(phi),sinf(phi)};
  relativePhaseMemory=remainderf(phi,2.0f*PI_F);
  alpha=scaled(reference,cosf(theta/2.0f));
  beta=scaled(multiply(reference,offset),sinf(theta/2.0f));
  normalizeState();
}
void beginEncoders() {
  Encoder *encoders[]={&probabilityEncoder,&phaseEncoder};
  for(auto encoder:encoders) {
    pinMode(encoder->pinA,INPUT_PULLUP);
    pinMode(encoder->pinB,INPUT_PULLUP);
    encoder->previous=(digitalRead(encoder->pinA)<<1)|digitalRead(encoder->pinB);
    encoder->rest=encoder->previous;
    encoder->quarters=0;
    encoder->pending=0;
    attachInterruptArg(encoder->pinA,encoderChanged,encoder,CHANGE);
    attachInterruptArg(encoder->pinB,encoderChanged,encoder,CHANGE);
  }
}
void pollEncoders() {
  portENTER_CRITICAL(&encoderMux);
  int32_t balanceClicks=probabilityEncoder.pending;
  int32_t phaseClicks=phaseEncoder.pending;
  probabilityEncoder.pending=0;
  phaseEncoder.pending=0;
  portEXIT_CRITICAL(&encoderMux);
  if(!balanceClicks && !phaseClicks) return;
  float p0=fminf(1.0f,fmaxf(0.0f,probability(alpha)));
  float oldTheta=p0<=QUBIT_EPSILON?PI_F:
                 probability(beta)<=QUBIT_EPSILON?0.0f:2.0f*acosf(sqrtf(p0));
  float theta=fminf(PI_F,fmaxf(0.0f,oldTheta+balanceClicks*PROBABILITY_STEP));
  bool balanceChanged=fabsf(theta-oldTheta)>1e-6f;
  float phi=remainderf(relativePhaseMemory+phaseClicks*PHASE_STEP,2.0f*PI_F);
  // A phase-only turn at a pole stores phi without rotating the survivor.
  // The phase takes visible effect when both circles have nonzero size.
  if(balanceChanged) setKnobAngles(theta,phi);
  else if(phaseClicks) {
    if(probability(alpha)>QUBIT_EPSILON && probability(beta)>QUBIT_EPSILON)
      setKnobAngles(theta,phi);
    else relativePhaseMemory=phi;
  }
  // No angle change at a hard stop: leave both complex amplitudes untouched.
  Serial.printf("Encoders: balance=%ld phase=%ld; phase setting=%.0f deg\n",
                (long)balanceClicks,(long)phaseClicks,
                fmodf(relativePhaseMemory*180.0f/PI_F+360.0f,360.0f));
  showState();
}

// Poll between animations; one command per press, no hold repeat.
// Scan every input before running a blocking animation. Simultaneous presses
// select the first button in the table; release and press again to retry.
// A complete press/release during an animation may be missed.
void pollButtons() {
  uint32_t now=millis();
  char pending=0;
  for(auto &button:buttons) {
    bool reading=digitalRead(button.pin);
    if(reading!=button.raw) {
      button.raw=reading;
      button.changedAt=now;
    }
    if(reading!=button.stable &&
       (uint32_t)(now-button.changedAt)>=BUTTON_DEBOUNCE_MS) {
      button.stable=reading;
      if(reading==LOW && !pending) pending=button.command;
    }
  }
  if(pending) {
    Serial.printf("Button pressed: %c\n",pending);
    applyCommand(pending);
  }
}

void setup() {
  Serial.begin(115200);
  delay(1200);
  randomSeed((uint32_t)micros());
  for(auto &button:buttons) {
    pinMode(button.pin,INPUT_PULLUP);
    // Held at boot: release before the first command can trigger.
    button.raw=button.stable=digitalRead(button.pin);
    button.changedAt=millis();
  }
  beginEncoders();
  pinMode(PIN_CS_0,OUTPUT);
  pinMode(PIN_CS_1,OUTPUT);
  digitalWrite(PIN_CS_0,HIGH);
  digitalWrite(PIN_CS_1,HIGH);
  SPI.begin(PIN_SCK,-1,PIN_MOSI,PIN_CS_0);
  lcd0.begin(SPI_HZ);
  lcd1.begin(SPI_HZ);
  Serial.println("My First Qubit - browser-matched gate animation");
  Serial.println("Type X, Y, Z, H, M, R, or C (colors) and press Send.");
  Serial.println("Buttons to GND: H=4 X=5 Y=6 Z=7 M=15 R=16 C=17");
  Serial.println("Encoders A/B: balance=1/2 phase=41/42; common pins to GND");
  showState();
}

void loop() {
  while(Serial.available()) {
    char c=(char)Serial.read();
    if(c=='\n'||c=='\r'||c==' '||c=='\t') continue;
    applyCommand((char)toupper((unsigned char)c));
  }
  pollButtons();
  pollEncoders();
  delay(1);
}
