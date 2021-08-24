#define MAX_DAC 4095
#define LOWVAL (MAX_DAC * 2000 / 3300)
#define HIVAL (MAX_DAC * 3200 / 3300)
#define RAMP_PERIOD  20000 // microseconds

int i = LOWVAL;
volatile bool is_intrpt = false;
bool is_intrpt_cpy = false;

IntervalTimer DAC_gen;
void int_func() {
  is_intrpt = true;
}

void setup() {
  analogWriteResolution(12);
  DAC_gen.begin(int_func, RAMP_PERIOD / (HIVAL - LOWVAL));  // int_func to run every 40 us
}

void loop() {
  mke_cpy();

  if (is_intrpt_cpy) {
    update_DAC();
    is_intrpt = false;
    is_intrpt_cpy = false;
  }
}

void mke_cpy() {
  noInterrupts();
  is_intrpt_cpy = is_intrpt;
  interrupts();
}

void update_DAC() {
  analogWrite(A14, i);
  i++;
  if (i > HIVAL) {
    i = LOWVAL;
  }
}
