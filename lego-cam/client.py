import cv2
import numpy as np
import socket
import struct
from io import BytesIO

# Capture frame
cap = cv2.VideoCapture(0)

# Set desired frame rate (FPS)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 768)
cap.set(cv2.CAP_PROP_FPS, 30)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.0.50', 8080))

while cap.isOpened():
    _, frame = cap.read()

    memfile = BytesIO()
    np.save(memfile, frame)
    memfile.seek(0)
    data = memfile.read()

    # Send form byte array: frame size + frame content
    client_socket.sendall(struct.pack("L", len(data)) + data)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
