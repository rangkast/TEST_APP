import socket
import cv2
import numpy as np
from PIL import Image, ImageDraw
# Configure the server
server_address = ("localhost", 8501)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(server_address)
sock.listen(1)

print("Waiting for a connection...")
connection, client_address = sock.accept()

try:
    print("Connection from:", client_address)
    # Receive image data from the client
    received_data = bytearray()
    while True:
        chunk = connection.recv(256000)
        if not chunk:
            break
        received_data.extend(chunk)
    # print('data received')
    # print(received_data)
    # Convert the received data to a numpy array (use OpenCV)
    input_image = cv2.imdecode(np.frombuffer(received_data, np.uint8), cv2.IMREAD_GRAYSCALE)
    # Perform image processing
    processed_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    # img = Image.fromarray(received_data)
    cv2.imshow('from ohmd', input_image)


    cv2.waitKey(1)

    # Send processed image data back to the client
    # processed_image_data = cv2.imencode(".bmp", processed_image)[1].tobytes()
    # connection.sendall(processed_image_data)

finally:
    # Clean up the connection
    connection.close()
    sock.close()
