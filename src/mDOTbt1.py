# This code connects to and streams Free Acceleration Data from one of the Movella DOT IMUs

import numpy as np
import asyncio
from bleak import BleakClient

# Service UUID's are based on the documentation like those shown below. How you interpret the documentation is that the Hexademimal codes given are the last four numbers of the characteristic uuid
# i.e. 15172001-4947-11e9-8646-d663bd873d93 has the UUID 0x2001 signifying it is the Control Service. Similarly, 15172004-4947-11e9-8646-d663bd873d93 corresponds to to the
# short payload length service 0x2004. Note how everything stays the same except for the last four digits of the first 8 numbers. The base UUID forthe Movella DOT's is located
# at the top of the BLE Services Specification document and is 1517xxxx-4947-11E9-8646-D663BD873D93 
measurement_characteristic_uuid = '15172001-4947-11e9-8646-d663bd873d93'
short_payload_characteristic_uuid = "15172004-4947-11e9-8646-d663bd873d93"

#This function is what actually prints the data out, and it requires a sender and data to print messages
def notification_callback(sender, data):
    #print(f"Sender: {sender}")
    #print(f"Data: {data}")
    #print(f'Encoded Free Acceleration: {encode_free_acceleration(data)}')
    print(encode_free_acceleration(data))

# The data that is actually streamed is encoded gibberish so we have to decrypt the data so that it reads actual acceleration data. It prints the information as bytes.
# According to the BLE specifications fro the DOTS, the short payload characteristic service that we are using always sends 20 bytes of data over the onnection.
# The free acceleration is reported as being 16 bytes in size and contains a timestamp and free acceleration. So the format of the data is this:
# The first four bytes is the timestamp according to a system clock, the next four bytes is x_acc, the next is y_acc, the next is z_acc, and since the payload has to be 20
# bytes long even though we are just sending 16, the last four bytes are unused so they are just set to 0's as 0x00
def encode_free_acceleration(bytes_):
    # These bytes are grouped according to Movella's BLE specification doc
    data_segments = np.dtype([
        ('timestamp', np.uint32),
        ('x', np.float32),
        ('y', np.float32),
        ('z', np.float32),
        ('zero_padding', np.uint32)
        ])
    formatted_data = np.frombuffer(bytes_, dtype=data_segments)
    return formatted_data

async def main():
    address = "D4:22:CD:00:8C:50" # Movella DOT Mac Address

    async with BleakClient(address) as client:
        # Check if connection was successful
        print(f"Client connection: {client.is_connected}") # prints True or False

        # Subscribe to notifications from the Short Payload Characteristic
        await client.start_notify(short_payload_characteristic_uuid, notification_callback)

        # Set and turn on the Free Acceleration measurement mode Note: THat changing the mode is by modifying the last x00 bit i.e. x06 = free aceleration mode
        binary_message = b"\x01\x01\x06"
        await client.write_gatt_char(measurement_characteristic_uuid, binary_message, response=True) # You may not need Response=True but I was unable to get the script working without it

        await asyncio.sleep(10.0)

asyncio.run(main())
