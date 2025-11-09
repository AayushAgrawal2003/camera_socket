import socket
import cv2
import numpy as np

HOST = "127.0.0.1"
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}")
client_socket, addr = server_socket.accept()
print(f"Connected to {addr}")

# Read transfer mode
mode_flag = client_socket.recv(1)
raw_mode = (mode_flag == b'R')
print("Mode:", "RAW" if raw_mode else "JPEG")

def recv_n(sock, n):
    data = b""
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

while True:
    # Read camera index first
    cam_index_bytes = recv_n(client_socket, 4)
    if cam_index_bytes is None:
        break
    cam_index = int.from_bytes(cam_index_bytes, 'big')

    if raw_mode:
        # Receive frame shape and data
        h = int.from_bytes(recv_n(client_socket, 4), 'big')
        w = int.from_bytes(recv_n(client_socket, 4), 'big')
        c = int.from_bytes(recv_n(client_socket, 4), 'big')
        length = int.from_bytes(recv_n(client_socket, 4), 'big')

        raw = recv_n(client_socket, length)
        if raw is None:
            break

        frame = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, c))

    else:
        # JPEG mode
        length = int.from_bytes(recv_n(client_socket, 4), 'big')
        data = recv_n(client_socket, length)
        if data is None:
            break

        frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
        # print(frame.shape)

    # Show window named by camera index
    cv2.imshow(f"Camera {cam_index}", frame)
    # print(f"Got data for {cam_index}")

    if cv2.waitKey(1) == ord('q'):
        break

client_socket.close()
server_socket.close()
cv2.destroyAllWindows()
