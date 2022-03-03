#define LED 23

const byte numChars = 32;
char recvBuffer[numChars];

boolean newData = false;

void setup()
{
  Serial.begin(9600);
  pinMode(LED, OUTPUT);
}

void loop()
{
  recieve();
  exec();
}

void recieve()
{
  static boolean receiving = false;
  static byte ndx = 0;
  char startch = '<';
  char endch = '>';
  char rc;

  while ((Serial.available() > 0) && (newData == false))
  {
    rc = Serial.read();
    if (receiving == true) // Receiving verifies if starting character was received. Characters are ignored until startch is detected.
    {
      if (rc != endch)
      {
        recvBuffer[ndx] = rc;
        ndx++;
        if (ndx == numChars)
        {
          ndx = numChars - 1;
        }
      }
      else
      { // End storing if ending character is received
        recvBuffer[ndx] = '\0';
        receiving = false;
        ndx = 0;
        newData = true;
      }
    }
    else if (rc == startch)
    { // Start storing if starting character is detected
      receiving = true;
    }
  }
}

// <G>
// <S&0>
// <S&1>
void exec()
{
  if (newData == true)
  {
    String dato = recvBuffer;
    String op = getValue(dato, '&', 0); // Get instruction type
    if (op.equals("G"))
    {
      Serial.println(digitalRead(LED));
    }
    else if (op.equals("S"))
    {
      int target = getValue(dato, '&', 1).toInt();
      digitalWrite(LED, target);
      Serial.println(digitalRead(LED));
    }
    newData = false;
  }
}

String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++)
  {
    if (data.charAt(i) == separator || i == maxIndex)
    {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}
