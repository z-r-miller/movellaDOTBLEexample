# stream.py 

import numpy as np
import asyncio
from bleak import BleakClient

measurement_characteristic_uuid = '15172001-4947-11e9-8646-d663bd873d93'
short_payload_characteristic_uuid = "15172004-4947-11e9-8646-d663bd873d93"

def notification_callback(sender, data):
    #print(f"Sender: {sender}")
    #print(f"Data: {data}")
    #print(f'Encoded Free Acceleration: {encode_free_acceleration(data)}')
    print(encode_quaternions(data))

def encode_quaternions(bytes_):
    # These bytes are grouped according to Movella's BLE specification doc
    data_segments = np.dtype([
        ('timestamp', np.uint32),
        ('w', np.float32),
        ('x', np.float32),
        ('y', np.float32),
        ('z', np.float32),
        ])
    formatted_data = np.frombuffer(bytes_, dtype=data_segments)
    return formatted_data

async def main():
    address = "D4:22:CD:00:8A:91" # Movella DOT Mac Address

    async with BleakClient(address) as client:
        # Check if connection was successful
        print(f"Client connection: {client.is_connected}") # prints True or False

        # Subscribe to notifications from the Short Payload Characteristic
        await client.start_notify(short_payload_characteristic_uuid, notification_callback)

        # Set and turn on the Quaternion measurement mode
        # Note that when changing modes you need to turn the sensor fully off and on again before rerunning the script
        binary_message = b"\x01\x01\x05"
        await client.write_gatt_char(measurement_characteristic_uuid, binary_message, response=True)

        await asyncio.sleep(10.0)

asyncio.run(main())
