import sys
from typing import cast, TypeVar
import argparse

TMessage = TypeVar("TMessage", bound="BaseMessage")

import cobs
from messages import *
from crc import crc

import asyncio
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from pydantic import BaseModel
from fastapi import Request


SCAN_TIMEOUT = 130.0
"""How long to scan for devices before giving up (in seconds)"""

SERVICE = "0000fd02-0000-1000-8000-00805f9b34fb"
"""The SPIKE™ Prime BLE service UUID"""

RX_CHAR = "0000fd02-0001-1000-8000-00805f9b34fb"
"""The UUID the hub will receive data on"""

TX_CHAR = "0000fd02-0002-1000-8000-00805f9b34fb"
"""The UUID the hub will transmit data on"""

DEVICE_NOTIFICATION_INTERVAL_MS = 5000
"""The interval in milliseconds between device notifications"""

EXAMPLE_SLOT = 0
"""The slot to upload the example program to"""

EXAMPLE_PROGRAM = """
import runloop, sys
from hub import light_matrix

async def main():
    await light_matrix.write("Yup!")
    print("done")
    sys.exit(0)

    
runloop.run(main())
""".encode(
    "utf8"
)
"""The utf8-encoded example program to upload to the hub"""

# answer = input(
#     f"This example will override the program in slot {EXAMPLE_SLOT} of the first hub found. Do you want to continue? [Y/n] "
# )
# if answer.strip().lower().startswith("n"):
#     print("Aborted by user.")
#     sys.exit(0)

stop_event = None
 


# serialize and pack a message, then send it to the hub
async def send_message(message: BaseMessage) -> None:
    global client, rx_char

    print(f"Sending: {message}")
    payload = message.serialize()
    frame = cobs.pack(payload)

    # use the max_packet_size from the info response if available
    # otherwise, assume the frame is small enough to send in one packet
    packet_size = info_response.max_packet_size if info_response else len(frame)

    # send the frame in packets of packet_size
    for i in range(0, len(frame), packet_size):
        packet = frame[i : i + packet_size]
        await client.write_gatt_char(rx_char, packet, response=False)


# simple response tracking
pending_response: tuple[int, asyncio.Future] = (-1, asyncio.Future())

# send a message and wait for a response of a specific type
async def send_request(
    message: BaseMessage, response_type: type[TMessage]
) -> TMessage:
    # nonlocal pending_response
    global pending_response
    pending_response = (response_type.ID, asyncio.Future())
    await send_message(message)
    return await pending_response[1]


# callback for when data is received from the hub
def on_data(_: BleakGATTCharacteristic, data: bytearray) -> None:
    if data[-1] != 0x02:
        # packet is not a complete message
        # for simplicity, this example does not implement buffering
        # and is therefore unable to handle fragmented messages
        un_xor = bytes(map(lambda x: x ^ 3, data))  # un-XOR for debugging
        print(f"Received incomplete message:\n {un_xor}")
        return

    data = cobs.unpack(data)
    
    global pending_response, stop_event
    try:
        message = deserialize(data)
        print(f"Received: {message}")
        if message.ID == pending_response[0]:
            pending_response[1].set_result(message)

        if isinstance(message, ConsoleNotification) and message.text == "done" :
            print("console:" + message.text)
            stop_event.set()
        
        if isinstance(message, DeviceNotification):

            # sort and print the messages in the notification
            updates = list(message.messages)
            updates.sort(key=lambda x: x[1])
            lines = [f" - {x[0]:<10}: {x[1]}" for x in updates]
            print("\n".join(lines))

    except ValueError as e:
        print(f"Error: {e}")


def on_disconnect(client: BleakClient) -> None:
    print("Connection lost.")
    stop_event.set()

def match_service_uuid(device: BLEDevice, adv: AdvertisementData) -> bool:
    # print(list(adv.service_uuids) + list(adv.manufacturer_data.items()))
    return SERVICE.lower() in adv.service_uuids

# to be initialized
info_response: InfoResponse = None
rx_char = None
tx_char = None
client = None
running = False

parser = argparse.ArgumentParser(description="Upload a program to SPIKE™ Prime hub over BLE.")
parser.add_argument('--program', type=str, help='String block to upload as the program. If omitted, uses the default example.')
args = parser.parse_args()

PROGRAM_TO_UPLOAD = None
if args.program:
    file = args.program.encode("utf8")
    with open(args.program, "rb") as f:
        PROGRAM_TO_UPLOAD = f.read()
else:
    PROGRAM_TO_UPLOAD = EXAMPLE_PROGRAM

class ScriptRequest(BaseModel):
    script: str

async def main():

    print(f"\nScanning for {SCAN_TIMEOUT} seconds, please wait...")
    device = await BleakScanner.find_device_by_filter(
        filterfunc=match_service_uuid, timeout=SCAN_TIMEOUT
    )

    if device is None:
        print(
            "No hubs detected. Ensure that a hub is within range, turned on, and awaiting connection."
        )
        sys.exit(1)

    device = cast(BLEDevice, device)
    print(f"Hub detected! {device}")

    print("Connecting...")
    global client, rx_char, tx_char, info_response
    client = BleakClient(device, disconnected_callback=on_disconnect)
    await client.connect()
    print("Connected!\n")

    service = client.services.get_service(SERVICE)

    rx_char = service.get_characteristic(RX_CHAR)
    tx_char = service.get_characteristic(TX_CHAR)

    # enable notifications on the hub's TX characteristic
    await client.start_notify(tx_char, on_data)

    # first message should always be an info request
    # as the response contains important information about the hub
    # and how to communicate with it
    info_response = await send_request(InfoRequest(), InfoResponse)

    # enable device notifications
    notification_response = await send_request(
        DeviceNotificationRequest(DEVICE_NOTIFICATION_INTERVAL_MS),
        DeviceNotificationResponse,
    )
    if not notification_response.success:
        print("Error: failed to enable notifications")
        sys.exit(1)
    
    print("p1")

    # await runprogram()
    # await runprogram()
    
    # await client.disconnect()


async def runprogram(programScript: str = PROGRAM_TO_UPLOAD):
    global stop_event
    stop_event = asyncio.Event()

    # clear the program in the example slot
    clear_response = await send_request(
        ClearSlotRequest(EXAMPLE_SLOT), ClearSlotResponse
    )
    if not clear_response.success:
        print(
            "ClearSlotRequest was not acknowledged. This could mean the slot was already empty, proceeding..."
        )

    # start a new file upload
    program_crc = crc(programScript)
    start_upload_response = await send_request(
        StartFileUploadRequest("program.py", EXAMPLE_SLOT, program_crc),
        StartFileUploadResponse,
    )
    if not start_upload_response.success:
        print("Error: start file upload was not acknowledged")
        sys.exit(1)

    # transfer the program in chunks
    running_crc = 0
    for i in range(0, len(programScript), info_response.max_chunk_size):
        chunk = programScript[i : i + info_response.max_chunk_size]
        running_crc = crc(chunk, running_crc)
        chunk_response = await send_request(
            TransferChunkRequest(running_crc, chunk), TransferChunkResponse
        )
        if not chunk_response.success:
            print(f"Error: failed to transfer chunk {i}")
            sys.exit(1)

    # start the program
    start_program_response = await send_request(
        ProgramFlowRequest(stop=False, slot=EXAMPLE_SLOT), ProgramFlowResponse
    )
    if not start_program_response.success:
        print("Error: failed to start program")
        sys.exit(1)
    
    await stop_event.wait()


import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks


app = FastAPI()

@app.post("/exec")
async def exec_script(request: Request):
    script = await request.body()
    print(script)
    if script:
        await runprogram(script)
    return {"status": "done"}

@app.get("/status")
async def status():
    return {"scan": "aaa"}


if __name__ == "__main__":
    from uvicorn import Config, Server

    async def run_uvicorn():
        config = Config(app, host="0.0.0.0", port=8000, loop="asyncio")
        server = Server(config)
        await server.serve()

    async def main_concurrent():
        await asyncio.gather(
            main(),
            run_uvicorn()
        )

    asyncio.run(main_concurrent())

