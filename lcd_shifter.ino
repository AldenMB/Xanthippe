
const int backplane2Pin = 2;
const int backplane3Pin = 3;
const int dataPins[] = {4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19};

volatile bool measurement[4][14];
volatile unsigned long lastReadTime = 0;
volatile unsigned long lastCompleteTime = 0;
volatile byte mostRecentMeasurement[14];
volatile int previousMeasurementJ = 3;

void setup() {
  pinMode(backplane2Pin, INPUT);
  pinMode(backplane3Pin, INPUT);
  attachInterrupt(digitalPinToInterrupt(backplane2Pin), read_ISR_backplane_2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(backplane3Pin), read_ISR_backplane_3, CHANGE);
  for(int i=0; i<14; ++i){
    pinMode(dataPins[i], INPUT);
  }
}

void loop() {
  // get something here to handle communication
}

void read_ISR_backplane_2(){
  read_ISR(false);
}
void read_ISR_backplane_3(){
  read_ISR(true);
}

void read_ISR(bool firstHalf){
  unsigned long now = millis();
  unsigned long delay = now - lastReadTime;
  if(delay < 2){ //debouncing
    return;
  }
  int j = firstHalf ? 1 - digitalRead(backplane3Pin) : 3 - digitalRead(backplane2Pin);
  int difference = j - previousMeasurementJ;
  if(!(j == 0 || (delay < 12 && difference == 1))){ // came in at a bad time
    return;
  }
  
  for(int i = 0; i<14; ++i){
    measurement[j][i] = digitalRead(dataPins[i]);
  }
  lastReadTime = now;
  previousMeasurementJ = j;
  if(j == 3){
    for(int i=0; i<14; ++i){
      byte entry = 0;
      for(int k=0; k<4; ++k){
        entry  = (entry << 1) | (byte)(measurement[k][i]);
      }
      mostRecentMeasurement[i] = entry;
    }
    lastCompleteTime = now;
  }
}
