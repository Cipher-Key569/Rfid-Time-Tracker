#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 53
#define RST_PIN 5
#define BUZZER_PIN 8

MFRC522 rfid(SS_PIN, RST_PIN);

// =========================
// AUTHORIZED RFID CARDS
// =========================

byte exampleUID1[] = {
  0x11, 0x22, 0x33, 0x44
};

byte exampleUID2[] = {
  0xAA, 0xBB, 0xCC, 0xDD
};
bool signedIn = false;
bool cardWasPresent = false;

void beep(int duration) {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(duration);
  digitalWrite(BUZZER_PIN, LOW);
}

void setup() {

  Serial.begin(9600);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  SPI.begin();
  rfid.PCD_Init();

  delay(100);

  Serial.println("RFID TIME TRACKER READY");
  Serial.println("Scan card...");
}

void loop() {

  if (!rfid.PICC_IsNewCardPresent()) {
    cardWasPresent = false;
    return;
  }

  if (cardWasPresent) {
    return;
  }

  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  cardWasPresent = true;

  if (isAuthorizedCard()) {

    if (!signedIn) {

      signedIn = true;

      Serial.print("SIGN_IN,");
      printUID();
      Serial.println();

      // One beep = sign in
      beep(150);

    } else {

      signedIn = false;

      Serial.print("SIGN_OUT,");
      printUID();
      Serial.println();

      // Two beeps = sign out
      beep(150);
      delay(150);
      beep(150);
    }

  } else {

    Serial.print("ACCESS_DENIED,");
    printUID();
    Serial.println();

    // Long beep = unknown card
    beep(500);
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  delay(500);
}

void printUID() {

  for (byte i = 0; i < rfid.uid.size; i++) {

    if (rfid.uid.uidByte[i] < 0x10) {
      Serial.print("0");
    }

    Serial.print(rfid.uid.uidByte[i], HEX);

    if (i < rfid.uid.size - 1) {
      Serial.print(":");
    }
  }
}

bool isAuthorizedCard() {

  byte* authorizedCards[] = {
    exampleUID1,
    exampleUID2
  };

  byte authorizedSizes[] = {
    sizeof(exampleUID1),
    sizeof(exampleUID2)
  };

  for (byte card = 0; card < 2; card++) {

    if (rfid.uid.size != authorizedSizes[card]) {
      continue;
    }

    bool match = true;

    for (byte i = 0; i < authorizedSizes[card]; i++) {

      if (rfid.uid.uidByte[i] != authorizedCards[card][i]) {
        match = false;
        break;
      }
    }

    if (match) {
      return true;
    }
  }

  return false;
}