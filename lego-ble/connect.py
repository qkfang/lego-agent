import asyncio
from bleak import BleakScanner, BleakClient

# LEGO SPIKE Prime Hub BLE UUIDs
SERVICE_UUID = "0000FD02-0000-1000-8000-00805F9B34FB"
RX_CHAR_UUID = "0000FD02-0001-1000-8000-00805F9B34FB"
TX_CHAR_UUID = "0000FD02-0002-1000-8000-00805F9B34FB"

async def notification_handler(sender, data):
    print(f"Notification from {sender}: {data.hex()}")

async def connect_and_listen():
    print("Scanning for LEGO SPIKE Prime Hub...")
    devices = await BleakScanner.discover()
    hub = None
    for d in devices:
        if SERVICE_UUID.lower() in [s.lower() for s in d.metadata.get("uuids", [])]:
            hub = d
            break
    if not hub:
        print("LEGO SPIKE Prime Hub not found.")
        return
    print(f"Found device: {hub.name} ({hub.address})")
    async with BleakClient(hub.address) as client:
        print("Connected. Enabling notifications on TX characteristic...")
        await client.start_notify(TX_CHAR_UUID, notification_handler)
        print("Notifications enabled. You can now send data.")
        # Example: send a command (replace with actual data as needed)
        # await client.write_gatt_char(RX_CHAR_UUID, b'\x01\x02', response=False)
        print("Press Ctrl+C to exit.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Disconnecting...")
        await client.stop_notify(TX_CHAR_UUID)

if __name__ == "__main__":
    asyncio.run(connect_and_listen())