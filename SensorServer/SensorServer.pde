// Copyright (c) 2010, Ward Cunningham
// Released under GPL v2

#include <Ethernet.h>
#include <OneWire.h>
#define num(array) (sizeof(array)/sizeof(array[0]))

byte mac[] = { 0xEE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED   };
byte ip[] = { 10, 0, 3, 201   };
char query[64];


Server server(80);
Client client(255);
OneWire ds(8);  // data pin

struct Temp {
  unsigned int code;
  int data;
} temp[32] = {{0,0}};

struct Pin {
  boolean present;
  int data;
} analog[6] = {{0,0}}, bynase[6] = {{0,0}};

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
  content("plain");
  emitJson();
}

void jsonpReport() {
  content("javascript");
  client.print(query);
  client.print("(");
  emitJson();
  client.print(")\n");
}

void emitJson() {
  client.println("{");
  for (int i = 0; i < num(analog); i++) {
    if (analog[i].present) {
      ikey('a',i);
      val(analog[i].data);
    }
  }
  for (int i=2; i<num(bynase); i++) {
    if (bynase[i].present) {
      ikey('b',i);
      val(bynase[i].data);
    }
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

void content(char* type) {
  client.print("HTTP/1.1 200 OK\nContent-Type: text/");
  client.print(type);
  client.print("\n\n");
}

void flotReport () {
    content("html");
    client.println("<html><head><meta name=viewport content=\"width=420;\" />");
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
  if (code == 'j') jsonReport();
  if (code == 'p') jsonpReport();
  if (code == ' ') flotReport();
}

void analogSample() {
  for (int i = 0; i < num(analog); i++) {
    analog[i].data = analogRead(i);
    analog[i].present |= (analog[i].data != 0);
  }
}

void bynaseSample() {
  for (int i=0; i<num(bynase); i++) {
    bynase[i].data = 0;
  }
  for (int t=0; t<1023; t++) {
    for (int i=0; i<num(bynase); i++) {
      bynase[i].data += digitalRead(i);
      bynase[i].present |= (bynase[i].data != 0);
    }
    delayMicroseconds(60);
  }
}

byte data[12];

void tempSample() {
  pinMode(7,OUTPUT);
  digitalWrite(7,HIGH);
  ds.reset_search();
  while(ds.search(data)) {
    tempReadDevice();
  }
  digitalWrite(7,LOW);
  Serial.println("");
  ds.reset();
  ds.write(0xCC,1);               // skip ROM, do simultaneous conversions
  ds.write(0x44,1);               // start conversion, with parasite power on at the end
}

void tempReadDevice() {
  if (crc_err(7)) return;
  if (0x28 != data[0]) return;
  unsigned int id = data[2]*256u+data[1];
  Serial.print(id);
  Serial.print(" ");
  int ch = channel (id);
  ds.reset();
  ds.select(data);
  pinMode(9,OUTPUT);          // Scope Sync
  digitalWrite(9,HIGH);
  ds.write(0xBE);             // Read Scratchpad
  digitalWrite(9,LOW);
  for (int i = 0; i < 9; i++) {
    data[i] = ds.read();
  }
  if (crc_err(8)) return;
  temp[ch].data = data[1]*256+data[0];
  temp[ch].code = id;      // don't set this too early or we could report bad data
  Serial.print(temp[ch].data);
  Serial.print(" ");
}

boolean crc_err(byte size) {
  if (OneWire::crc8(data, size) != data[size]) {
      crc_errs++;
      Serial.print("crc ");
    return true;
  } else {
    return false;
  }
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
    boolean amp = false;
    boolean equal = false;
    char code = 0;
    int i = 0;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        // Serial.print(c);
        if (c == '\n' && blank) {
          query[i++ & num(query)-1] = 0;
          report(code);
          break;
        }
        if (c == '\n') {
          blank = true;
        }
        else if (c != '\r') {
          blank = false;
          if (slash) {
            if (code == 0) {
              code = c;
            } else {
              if (equal) {
                if (amp || c == '&') {
                  amp = true;
                } else {
                  query[i++ & num(query)-1] = c;
                }
              }
            }
          }
          slash |= c == '/';
          equal |= c == '=';
        }
      }
    }
    client.stop();
  }
}
