import cv2
import depthai as dai
import socket
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--raw", action="store_true", help="Send raw uncompressed frames")
args = parser.parse_args()

HOST = '127.0.0.1'
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Send mode flag to receiver first
mode_flag = b'R' if args.raw else b'J'
client_socket.send(mode_flag)

with dai.Pipeline() as pipeline:
    cam = pipeline.create(dai.node.Camera).build()
    outputQueue = cam.requestOutput((640,400)).createOutputQueue()

    pipeline.start()
    while pipeline.isRunning():

        videoIn = outputQueue.get()
        assert isinstance(videoIn, dai.ImgFrame)

        frame = videoIn.getCvFrame()   # BGR numpy frame

        if args.raw:
            h, w, c = frame.shape
            data = frame.tobytes()

            client_socket.send(h.to_bytes(4, 'big'))
            client_socket.send(w.to_bytes(4, 'big'))
            client_socket.send(c.to_bytes(4, 'big'))
            client_socket.send(len(data).to_bytes(4, 'big'))
            client_socket.send(data)

        else:
            ret, jpeg_frame = cv2.imencode('.jpg', frame)
            if not ret:
                print("Encoding error")
                continue

            data = jpeg_frame.tobytes()
            client_socket.send(len(data).to_bytes(4, 'big'))
            client_socket.send(data)

        cv2.imshow("Sending Video", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

client_socket.close()
cv2.destroyAllWindows()
