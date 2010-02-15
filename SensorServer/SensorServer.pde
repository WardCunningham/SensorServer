// Copyright (c) 2010, Ward Cunningham
// Released under GPL v2

#include <Ethernet.h>
#include <OneWire.h>
#define num(array) (sizeof(array)/sizeof(array[0]))

byte mac[] = { 0xEE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED   };
byte ip[] = { 10, 0, 3, 201   };

Server server(80);
Client client(255);
OneWire ds(8);  // data pin

int analog[6];
int bynase[6];

struct Temp {
  unsigned int code;
  int data;
} temp[32] = {{0,0}};

unsigned int last = 100;
unsigned long requests = 0;
unsigned long crc_errs = 0;

void setup() {
  Serial.begin(9600);
  Ethernet.begin(mac, ip);
  server.begin();
}

void loop() {
  sample();    // every second or so
  serve();     // whenever web requests come in
}

void sample() {
  unsigned int now = millis();
  if ((now-last) >= 1000) {
    last = now;
    analogSample();
    bynaseSample();
    tempSample();
  }
}

void key(char prefix, unsigned int index) {
  client.print("\t\"");
  client.print(prefix);
  client.print(index);
  client.print("\":\t");
}

void ikey(char prefix, unsigned int index) {
  client.print("\t\"");
  client.print(prefix);
  client.print(ip[3],DEC);
  client.print(index);
  client.print("\":\t");
}

void val(int number) {
  client.print(number);
  client.println(",");
}

void uval(unsigned long number) {
  client.print(number);
  client.println(",");
}

void jsonReport() {
  client.print("HTTP/1.1 200 OK\nContent-Type: text/plain\n\n");
  client.println("{");
  for (int i = 0; i < num(analog); i++) {
    ikey('a',i);
    val(analog[i]);
  }
  for (int i=2; i<num(bynase); i++) {
    ikey('b',i);
    val(bynase[i]);
  }
  for (int ch=0; ch<num(temp); ch++) {
    if (temp[ch].code) {
      key('c',temp[ch].code);
      val(temp[ch].data);
    }
  }

  key('t',0); uval(millis());
  key('t',1); val(((unsigned int)millis()) - last);
  key('r',0); uval(requests);
  key('r',1); uval(crc_errs);

  client.println("}");
}
void script(char* script) {
  client.print("<script src=http://c2.com/ward/arduino/SensorServer/js/");
  client.print(script);
  client.println("></script>");
}

void flotReport () {
    client.println("HTTP/1.1 200 OK\nContent-Type: text/html\n\n<html><head>");
    client.println("<meta name=viewport content=\"width=420;\" />");
    script("jquery.js");
    script("jquery.timers.js");
    script("jquery.flot.js");
    script("ss.js");
    client.println("</head><body>");
    client.println("<h1>Live SensorServer Data</h1>");
    client.println("<div id=plot style=\"width:400px;height:300px;\"></div>");
    client.println("<div id=stat></div>");
    client.println("</body></html>\n");
}

void report(char code) {
  if (code>>3 == 'a'>>3) { // deprecated
    client.println("HTTP/1.1 200 OK\nContent-Type: text/plain\n\n");
    if (code & 1) analogReport();
    if (code & 2) bynaseReport();
    if (code & 4) tempReport();
  }
  if (code == 'j') jsonReport();
  if (code == ' ') flotReport();
}

void analogSample() {
  for (int i = 0; i < num(analog); i++) {
    analog[i] = analogRead(i);
  }
}

void analogReport() {
  client.print("analog");
  for (int i = 0; i < num(analog); i++) {
    client.print("\t");
    client.print(analog[i]);
  }
  client.print("\n");
}

void bynaseSample() {
  for (int i=0; i<num(bynase); i++) {
    bynase[i] = 0;
  }
  for (int t=0; t<1023; t++) {
    for (int i=0; i<num(bynase); i++) {
      bynase[i] += digitalRead(i);
    }
    delayMicroseconds(60);
  }
}

void bynaseReport() {
  client.print("bynase");
  for (int i=0; i<num(bynase); i++) {
    client.print("\t");
    client.print(bynase[i]);
  }
  client.print("\n");
}

byte data[12];
unsigned int id;
int ch = -1;

void tempSample() {
  pinMode(7,OUTPUT);
  digitalWrite(7,HIGH);
  while(1) {
    startTempSample();
    if (ch < 0) break;
    finishTempSample();
  }
  digitalWrite(7,LOW);
  ds.reset();
  ds.write(0xCC,1);               // skip ROM, do simultaneous conversions
  ds.write(0x44,1);               // start conversion, with parasite power on at the end
}

void startTempSample() {
  if (ch < 0) {
    ds.reset_search();
  }
  if (!ds.search(data)) {
    ch = -1;
    Serial.println("");
  }
  else {
    if (OneWire::crc8(data, 7) == data[7] && 0x28 == data[0]) {
      id = data[2]*256u+data[1];
      Serial.print(id);
      Serial.print(" ");
      ch = channel (id);
 //     ds.reset();
 //     ds.select(data);
 //     ds.write(0x44,1);         // start conversion, with parasite power on at the end
    } else {
      crc_errs++;
      Serial.print("crc   ");
    }
  }
}

void finishTempSample() {
  if (ch >= 0) {                // if we've discovered a devise and started a conversion
    ds.reset();
    ds.select(data);
    pinMode(9,OUTPUT);          // Scope Sync
    digitalWrite(9,HIGH);
    ds.write(0xBE);             // Read Scratchpad
    digitalWrite(9,LOW);
    for (int i = 0; i < 9; i++) {
      data[i] = ds.read();
    }
    if (OneWire::crc8(data, 8) == data[8]) {
      temp[ch].data = data[1]*256+data[0];
      Serial.print(temp[ch].data);
      Serial.print(" ");
      temp[ch].code = id;      // don't set this too early or we could report bad data
    } else {
      crc_errs++;
      Serial.print("crc ");
    }
  }
}

void tempReport() {
  client.print("18b20");
  for (int ch=0; ch<num(temp); ch++) {
    if (temp[ch].code) {
      client.print("\t");
      client.print(temp[ch].code);
      client.print(" ");
      client.print(temp[ch].data);
    }
  }
  client.print("\n");
}

int channel(int id) {
  for (int ch=0; ch<num(temp); ch++) {
    if (temp[ch].code == id || temp[ch].code == 0) {
      return ch;
    }
  }
  return 0;
}

void serve() {
  client = server.available();
  if (client) {
    requests++;
    boolean blank = true;
    boolean slash = false;
    char code = 0;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        // Serial.print(c);
        if (c == '\n' && blank) {
          report(code);
          break;
        }
        if (c == '\n') {
          blank = true;
        }
        else if (c != '\r') {
          blank = false;
          if (slash && code == 0) {
            code = c;
          }
          slash = c == '/';
        }
      }
    }
    client.stop();
  }
}
