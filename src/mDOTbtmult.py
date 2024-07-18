# Stream Free Acceleration data from multiple Movella DOTs

import numpy as np
import asyncio
from bleak import BleakClient

measurement_char_uuid = "15172001-4947-11e9-8646-d663bd873d93"
short_payload_char_uuid = "15172004-4947-11e9-8646-d663bd873d93"

# Replace this with a list of your DOT's UUID addresses 
# (or "MAC addresses" for Windows and Linux users)
addresses = [
    "D4:22:CD:00:8C:50",
    "D4:22:CD:00:8A:91"
]

class NotificationHandler:
    '''This class allows us to add the DOT's UUID address to the data that gets printed'''
    def __init__(self, device_address):
        self.device_address = device_address

    def callback(self, sender, data):
        free_acceleration = encode_free_acceleration(data)[0]
        free_acceleration = str(free_acceleration)[1:-1]
        print(f"{self.device_address} -- {free_acceleration}")

def encode_free_acceleration(bytes_):
    data_segments = np.dtype([
        ('timestamp', np.uint32),
        ('x', np.float32),
        ('y', np.float32),
        ('z', np.float32),
        ('zero_padding', np.uint32)
        ])
    formatted_data = np.frombuffer(bytes_, dtype=data_segments)
    return formatted_data

async def connect(address):
    nh = NotificationHandler(address)
    # Connect to the DOT and stream data
    async with BleakClient(address) as client:
        print(f"Client connection to `{client.address}: {client.is_connected}")
    
        # Subscribe to data notifications
        await client.start_notify(short_payload_char_uuid, nh.callback)

        # Set and turn on measurement mode
        binary_message = b"\x01\x01\x06"
        await client.write_gatt_char(measurement_char_uuid, binary_message, response=True)

        # Stream data for 10 seconds
        await asyncio.sleep(10.0)

async def main():
    await asyncio.gather(*(connect(addr) for addr in addresses))

if __name__ == "__main__":
    asyncio.run(main())
