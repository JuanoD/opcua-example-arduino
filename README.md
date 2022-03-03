# OPC-UA server example for an Arduino

A client/server architecture for communication between a microcontroller and an OPC-UA server.

The OPC-UA server acts as a client that polls the arduino for its state, or requests it to perform an action (In this example, turning on and off a LED).

Use Arduino IDE to compile and upload `server/server.ino` to the controller.

```
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
python client/opcua.py
```

This example uses [opcua-asyncio](https://github.com/FreeOpcUa/opcua-asyncio/) and [PySerial](https://github.com/pyserial/pyserial).
