const uint8_t dht_pin=2;

void sendStartSignal(){
    pinMode(dht_pin,OUTPUT);
    digitalWrite(dht_pin,LOW);
    delay(20);

    digitalWrite(dht_pin,HIGH);
    delayMicroseconds(40);
    pinMode(dht_pin,INPUT);
}

int measurePulse(uint8_t level,uint16_t timeout){
    uint32_t start=micros();
    while(digitalRead(dht_pin)==level){
      if(micros()-start>timeout) return -1;
    }

    return micros()-start;
}

bool sensorResponse(){
  if(measurePulse(HIGH,100)==-1) return false;
  if(measurePulse(LOW,100)==-1) return false;
  if(measurePulse(HIGH,100)==-1) return false;
  return true;

}

int8_t readBit(){
  //start condition when reading a bit;
  uint32_t start=micros();
  while(digitalRead(dht_pin)==0)
      if(micros()-start>100)//in case of timeout
        return -1;
  start=micros();
  while(digitalRead(dht_pin)==1)
      if(micros()-start>100)
        return -1;

  if(micros()-start>40) //treshold value,at the ~midpoint of 28 and 70
        return 1;
  return 0;
  
}

void readHT(uint8_t &h,uint8_t &t,bool &ok){
    sendStartSignal();

    if (!sensorResponse()) {
        Serial.println("No response");
        ok = false;
        return;
    }
    
    uint8_t data[5]={0};
    for(int i=0;i<40;i++){
      int8_t bit=readBit();
      if(bit==-1) 
      {
        Serial.println("Something wrong: ");
        Serial.println(i);
        ok=0;
        return;
      }
      data[i/8] = data[i/8] << 1;
      data[i/8] |= bit;
    }
    uint8_t sum = data[0]+ data[1] + data[2] + data[3];
    if(sum!=data[4])
    {
      Serial.println("Sum is wrong!");
      ok=0;
      return;
    }

    h=data[0];
    t=data[2];

    //the sensor pulls the line low,end of communication
    while(digitalRead(dht_pin)==0);

}
void setup() {
  Serial.begin(9600);
  delay(1000);
}

void loop() {
  uint8_t t,h;
  bool ok=1;
  readHT(h,t,ok);
  if(ok){
    Serial.print("Temp is ");
    Serial.print(t);
    Serial.println("C");
    Serial.print("Humidity is ");
    Serial.print(h);
    Serial.println("%");
  }
  delay(1000);
}
// void setup(){ Serial.begin(9600); pinMode(2, INPUT); }
// void loop(){ Serial.println(digitalRead(2)); delay(500); }
