#include <Ethernet.h>
#include <OneWire.h>

byte mac[] = { 
  0xEE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
byte ip[] = { 
  10, 0, 3, 201 };
Server server(80);
OneWire ds(8);  // data pin

void setup()
{
  Ethernet.begin(mac, ip);
  server.begin();
  Serial.begin(9600);
}

void loop()
{
  Client client = server.available();
  if (client) {
    // an http request ends with a blank line
    boolean current_line_is_blank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        Serial.print(c);
        // if we've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so we can send a reply
        if (c == '\n' && current_line_is_blank) {
          // send a standard http response header
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/plain");
          client.println();

          // output the value of each analog input pin
          analogScan(client);
          bynaseScan(client);
          tempScan(client);
          break;
        }
        if (c == '\n') {
          // we're starting a new line
          current_line_is_blank = true;
        } 
        else if (c != '\r') {
          // we've gotten a character on the current line
          current_line_is_blank = false;
        }
      }
    }
    client.stop();
  }
}

void analogScan(Client client) {
  client.print("analog");
  for (int i = 0; i < 6; i++) {
    client.print("\t");
    client.print(analogRead(i));
  }
  client.print("\n");
}

void bynaseScan(Client client) {
  int sum[8]={0};
  for (int t=0; t<1023; t++) {
    for (int i=0; i<8; i++) {
      sum[i] += digitalRead(i);
    }
    delayMicroseconds(60);
  }
  client.print("bynase");
  for (int i=0; i<8; i++) {
    client.print("\t");
    client.print(sum[i]);
  }
  client.print("\n");
}

void tempScan(Client client) {
  byte data[12];
  ds.reset_search();
  client.print("18b20");
  while (ds.search(data)){
    if (OneWire::crc8(data, 7) == data[7] && 0x28 == data[0]) {
      unsigned int id = data[2]*256u+data[1];
      ds.reset();
      ds.select(data);
      ds.write(0x44,1);         // start conversion, with parasite power on at the end
      delay(1000);              // maybe 750ms is enough, maybe not
      byte present = ds.reset();
      ds.select(data);
      ds.write(0xBE);          // Read Scratchpad
      for (int i = 0; i < 9; i++) {
        data[i] = ds.read();
      }
      if (OneWire::crc8(data, 8) == data[8]) {
        int c = data[1]*256+data[0];
        client.print("\t");
        client.print(id); 
        client.print(" ");
        client.print(c); 
      }
    }
  }
  client.print("\n");
}
