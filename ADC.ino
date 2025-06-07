const int adcPin = A0;       // Pin ADC tempat sinyal peak detector masuk
const int sampleCount = 100; // Jumlah pengambilan data per rata-rata

void setup() {
  Serial.begin(9600);
}

void loop() {
  unsigned long sum = 0;
  
  for (int i = 0; i < sampleCount; i++) {
    sum += analogRead(adcPin); // Baca nilai ADC
  }

  int avg = sum / sampleCount;  // Hitung rata-rata
  Serial.println(avg);          // Kirim hasil ke GUI

  // Tidak ada delay -> pembacaan terus berlangsung
}
