#include <DHT11.h>
#include <DHT.h>
// PrintWriter output;
// DHT11 setup
#define DHTPIN 2     // What digital pin the DHT11 is connected to
#define DHTTYPE DHT11   // DHT 11

DHT dht(DHTPIN, DHTTYPE);
int counter =0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(3,'OUTPUT');
  pinMode(A0,'INPUT');
  
  dht.begin();
  // output = createWriter( "data.txt" );
}

void loop() {
  // put your main code here, to run repeatedly:
  // output = open("C:\Users\kulkaekn\safedriftproximity\dataWrite.txt", "w+");
  // delay(2000);
  
 float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  int gasValue = analogRead(A0); 
  if (temperature >=40 || humidity <=45 || gasValue >=2)
  {
    digitalWrite(3,'HIGH');
    delay(5000);
   
  }
  
  
  
   int locationID = 0; // Example location ID stastic
   Serial.write("Counter: ");
  Serial.println(counter);
  counter = counter +1;
  // Send the data through the serial port
  Serial.print(humidity);
  Serial.print(",");
  Serial.print(temperature);
  Serial.print(",");
  Serial.print(gasValue);
  Serial.print(",");
  Serial.println(locationID);
  // output_file.write(humidity);
  //  output.flush();  // Writes the remaining data to the file
  // output.close();
  delay(1000);
}
