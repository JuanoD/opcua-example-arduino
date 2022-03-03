from asyncua import Server, uamethod, ua
from serial import Serial
import asyncio
import os

# Create class to wrap serial read and write async
class SafeSerial:
    def __init__(self, url: str, baudrate: int):
        self.url = url
        self.baudrate = baudrate
        self.serial = Serial(url, baudrate)
        self.lock = asyncio.Lock()
        self.status = True

    async def reset(self):
        self.serial = Serial(self.url, self.baudrate)
        self.status = True

    async def readline(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.serial.readline)

    async def write(self, data: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.serial.write, data)


def create_set_led(serial: SafeSerial):
    @uamethod
    async def set_led(parent, state: bool):
        loop = asyncio.get_event_loop()
        async with serial.lock:
            await serial.write(f"<S&{int(state)}>".encode())
            res = await serial.readline()
            return not not int(res.decode()[0])

    return set_led


async def main():
    # Create serial connection
    serial = SafeSerial(
        os.environ.get("SERIAL") if os.environ.get("SERIAL") else "COM3",
        os.environ.get("BAUD") if os.environ.get("BAUD") else 9600,
    )
    # Initialize OPC-UA Server
    server = Server()
    await server.init()
    server.set_endpoint(
        f"opc.tcp://localhost:{os.environ.get('PORT') if os.environ.get('PORT') else 4840}/freeopcua/server/"
    )
    # Instance method and state variable for LED
    uri = "test:opcua"
    idx = await server.register_namespace(uri)
    led_state = await server.nodes.objects.add_variable(idx, "LEDState", False)
    await server.nodes.objects.add_method(
        idx,
        "SetLEDState",
        create_set_led(serial),
        [ua.VariantType.Boolean],
        [ua.VariantType.Boolean],
    )

    # Initialize OPC-UA server
    async with server:
        await asyncio.sleep(0.1)
        # Pool for LED state
        while True:
            await asyncio.sleep(0.5)
            try:
                status: bool = None
                async with serial.lock:
                    await serial.write(b"<G>")
                    res = await serial.readline()
                    status = not not int(res.decode()[0])
                await led_state.set_value(status, ua.VariantType.Boolean)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    asyncio.run(main())
