import numpy as np
import asyncio
from bleak import BleakClient
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

measurement_characteristic_uuid = '15172001-4947-11e9-8646-d663bd873d93'
short_payload_characteristic_uuid = "15172004-4947-11e9-8646-d663bd873d93"

latest_euler_angles = None

def notification_callback(sender, data):
    global latest_euler_angles
    quaternion = encode_quaternions(data)
    if quaternion is not None:
        q = quaternion[0]
        latest_euler_angles = quaternion_to_euler(q['w'], q['x'], q['y'], q['z'])
        print(f"Received Euler Angles - Roll: {latest_euler_angles[0]}, Pitch: {latest_euler_angles[1]}, Yaw: {latest_euler_angles[2]}")

def encode_quaternions(bytes_):
    try:
        data_segments = np.dtype([
            ('timestamp', np.uint32),
            ('w', np.float32),
            ('x', np.float32),
            ('y', np.float32),
            ('z', np.float32),
        ])
        formatted_data = np.frombuffer(bytes_, dtype=data_segments)
        return formatted_data
    except Exception as e:
        print(f"Error in encoding quaternions: {e}")
        return None

def quaternion_to_euler(w, x, y, z):
    # Normalize quaternion
    norm = np.sqrt(w**2 + x**2 + y**2 + z**2)
    w, x, y, z = w / norm, x / norm, y / norm, z / norm
    
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll = np.arctan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)
    t2 = np.clip(t2, -1.0, +1.0)
    pitch = np.arcsin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw = np.arctan2(t3, t4)

    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)

def rotation_matrix_from_euler(roll, pitch, yaw):
    r = np.radians(roll)
    p = np.radians(pitch)
    y = np.radians(yaw)

    R_x = np.array([
        [1, 0, 0],
        [0, np.cos(r), -np.sin(r)],
        [0, np.sin(r), np.cos(r)]
    ])

    R_y = np.array([
        [np.cos(p), 0, np.sin(p)],
        [0, 1, 0],
        [-np.sin(p), 0, np.cos(p)]
    ])

    R_z = np.array([
        [np.cos(y), -np.sin(y), 0],
        [np.sin(y), np.cos(y), 0],
        [0, 0, 1]
    ])

    R = np.dot(R_z, np.dot(R_y, R_x))
    return R

async def plot_orientation():
    global latest_euler_angles
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    arrow_length = 0.5

    while True:
        if latest_euler_angles is not None:
            roll, pitch, yaw = latest_euler_angles
            R = rotation_matrix_from_euler(roll, pitch, yaw)

            # Define the arrow direction in the sensor's frame of reference
            arrow_direction = np.dot(R, np.array([1, 0, 0])) * arrow_length

            # Clear the plot and draw the new orientation
            ax.clear()
            ax.quiver(0, 0, 0, arrow_direction[0], arrow_direction[1], arrow_direction[2], color='r', length=arrow_length)
            ax.set_xlim([-1, 1])
            ax.set_ylim([-1, 1])
            ax.set_zlim([-1, 1])
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('Sensor Orientation')
            plt.draw()
            plt.pause(0.01)

        await asyncio.sleep(0.01)

async def main():
    address = "D4:22:CD:00:8A:91"  # Movella DOT Mac Address

    async with BleakClient(address) as client:
        print(f"Client connection: {client.is_connected}")  # prints True or False

        await client.start_notify(short_payload_characteristic_uuid, notification_callback)

        binary_message = b"\x01\x01\x05"
        await client.write_gatt_char(measurement_characteristic_uuid, binary_message, response=True)

        await plot_orientation()

        await asyncio.sleep(10.0)

asyncio.run(main())
