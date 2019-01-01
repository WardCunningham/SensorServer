
// ESP Wireless Sensor Server
//
// http://www.pjrc.com/teensy/td_libs_OneWire.html
// https://randomnerdtutorials.com/esp8266-ds18b20-temperature-sensor-web-server-with-arduino-ide/

#include <ESP8266WiFi.h>
#include <OneWire.h>

# define SENSORS 10
int  sensors=0, new_sensors=0;
long keys[SENSORS], new_keys[SENSORS];
int  vals[SENSORS], new_vals[SENSORS];
OneWire  ds(5);  // on pin 5 with 4.7k pullup

// Replace with your network details
const char* ssid = "Cunningham IOT";
const char* password = "password";
WiFiServer server(80);
WiFiClient client;


// A R D U I N O

void setup() {
  Serial.begin(9600); delay(100);
  start_server();
}

void loop() {
  next_sensor();
  next_client();
}


// S E N S O R

void sensor_value(long key, int val) {
  if (new_sensors + 1 == SENSORS) return;
  new_keys[new_sensors] = key;
  new_vals[new_sensors++] = val;
  Serial.print(key, HEX); Serial.print(" ");
  Serial.print(val); Serial.println();
}

void next_sensor_frame() {
  for(sensors=0; sensors<new_sensors; sensors++) {
    keys[sensors] = new_keys[sensors];
    vals[sensors] = new_vals[sensors];
  }
  new_sensors = 0;
}

void next_sensor() {
  byte i;
  byte present = 0;
  byte type_s;
  byte data[12];
  byte addr[8];
  long key = 0;
  
  if ( !ds.search(addr)) {
    Serial.println("No more addresses.");
    next_sensor_frame();
    ds.reset_search();
    delay(250);
    return;
  }
  
  if (OneWire::crc8(addr, 7) != addr[7]) {
      Serial.println("CRC is not valid!");
      return;
  }

  for(i=0; i<4; i++){
    key = (key << 8) + addr[i];
  }
 
  // the first ROM byte indicates which chip
  switch (addr[0]) {
    case 0x10: // Chip = DS18S20
      type_s = 1;
      break;
    case 0x28: // Chip = DS18B20
      type_s = 0;
      break;
    case 0x22: // Chip = DS1822
      type_s = 0;
      break;
    default:  // Device is not a DS18x20 family device
      return;
  } 

  ds.reset();
  ds.select(addr);
  ds.write(0x44, 1);        // start conversion, with parasite power on at the end
  
  delay(1000);              // maybe 750ms is enough, maybe not
  // we might do a ds.depower() here, but the reset will take care of it.
  
  present = ds.reset();
  ds.select(addr);    
  ds.write(0xBE);           // Read Scratchpad

  for ( i = 0; i < 9; i++) {  // we need 9 bytes
    data[i] = ds.read();
  }

  // Convert the data to actual temperature
  // because the result is a 16 bit signed integer, it should
  // be stored to an "int16_t" type, which is always 16 bits
  // even when compiled on a 32 bit processor.
  int16_t raw = (data[1] << 8) | data[0];
  if (type_s) {
    raw = raw << 3; // 9 bit resolution default
    if (data[7] == 0x10) {
      // "count remain" gives full 12 bit resolution
      raw = (raw & 0xFFF0) + 12 - data[6];
    }
  } else {
    byte cfg = (data[4] & 0x60);
    // at lower res, the low bits are undefined, so let's zero them
    if (cfg == 0x00) raw = raw & ~7;  // 9 bit resolution, 93.75 ms
    else if (cfg == 0x20) raw = raw & ~3; // 10 bit res, 187.5 ms
    else if (cfg == 0x40) raw = raw & ~1; // 11 bit res, 375 ms
    //// default is 12 bit resolution, 750 ms conversion time
  }
  
  sensor_value(key, raw);
}


// S E R V E R

void start_server() {
  Serial.print("\nMAC: "); Serial.println(WiFi.macAddress());
  Serial.print("\nSSID: "); Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  server.begin();
  delay(10000);
  Serial.print("\nIP: "); Serial.println(WiFi.localIP());
}

void next_client() {
  // Listenning for new clients
  client = server.available();
  if (client) {
    Serial.println("New client");
    // bolean to locate when the http request ends
    boolean blank_line = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        if (c == '\n' && blank_line) {
            client.println("HTTP/1.1 200 OK");
            client.println("Content-Type: application/json");
            client.println("Access-Control-Allow-Origin: *");
            client.println("Connection: close");
            client.println();
            print_json();
            break;
        }
        if (c == '\n') {
          // when starts reading a new line
          Serial.println();
          blank_line = true;
        }
        else if (c != '\r') {
          // when finds a character on the current line
          Serial.write(c);
          blank_line = false;
        }
      }
    }  
    // closing the client connection
    delay(1);
    client.stop();
    Serial.println("Client disconnected.");
  }
}

void print_json() {
  client.println("{");
  for (int i=0; i<sensors; i++) {
    client.print("\"");
    client.print(keys[i], HEX);
    client.print("\": ");
    client.print(vals[i]);
    if (i+1 < sensors) {
      client.println(",");
    } else {
      client.println();
    }
  }
  client.println("}");
}
