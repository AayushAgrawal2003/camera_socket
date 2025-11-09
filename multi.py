#!/usr/bin/env python3

import cv2
import depthai as dai
import contextlib
import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--raw", action="store_true", help="Send raw uncompressed frames")
args = parser.parse_args()

HOST = '127.0.0.1'
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Send mode flag once
mode_flag = b'R' if args.raw else b'J'
client_socket.send(mode_flag)

def createPipeline(pipeline):
    camRgb = pipeline.create(dai.node.Camera).build()
    # output = camRgb.requestOutput((640,400), dai.ImgFrame.Type.NV12 ,dai.ImgResizeMode.CROP, 20).createOutputQueue()
    output = camRgb.requestOutput((640,400)).createOutputQueue()
    return pipeline, output

with contextlib.ExitStack() as stack:
    deviceInfos = dai.Device.getAllAvailableDevices()
    print("=== Found devices: ", deviceInfos)
    queues = []
    pipelines = []

    # Build pipelines for every connected device
    for deviceIndex, deviceInfo in enumerate(deviceInfos):
        pipeline = stack.enter_context(dai.Pipeline())
        device = pipeline.getDefaultDevice()

        print("=== Connected to", deviceInfo.getDeviceId())
        mxId = device.getDeviceId()
        cameras = device.getConnectedCameras()
        usbSpeed = device.getUsbSpeed()
        eepromData = device.readCalibration2().getEepromData()
        print("   >>> Device ID:", mxId)
        print("   >>> Num of cameras:", len(cameras))
        if eepromData.boardName != "":
            print("   >>> Board name:", eepromData.boardName)
        if eepromData.productName != "":
            print("   >>> Product name:", eepromData.productName)

        pipeline, output = createPipeline(pipeline)
        pipeline.start()
        pipelines.append(pipeline)
        queues.append((deviceIndex, output))   # store index + queue
    print(queues)

    # Send frames
    while True:
        for deviceIndex, stream in queues:
            videoIn = stream.get()
            frame = videoIn.getCvFrame()  # BGR numpy

            if args.raw:
                h, w, c = frame.shape
                data = frame.tobytes()

                # Camera index
                client_socket.send(deviceIndex.to_bytes(4, 'big'))
                # Dimensions + data len
                client_socket.send(h.to_bytes(4, 'big'))
                client_socket.send(w.to_bytes(4, 'big'))
                client_socket.send(c.to_bytes(4, 'big'))
                client_socket.send(len(data).to_bytes(4, 'big'))
                client_socket.send(data)

            else:
                ret, jpeg_frame = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                data = jpeg_frame.tobytes()

                client_socket.send(deviceIndex.to_bytes(4, 'big'))
                client_socket.send(len(data).to_bytes(4, 'big'))
                client_socket.send(data)

            # cv2.imshow(f"Sending Video Device {deviceIndex}", frame)
            # print(f"Sent Data for {deviceIndex}")

        if cv2.waitKey(1) == ord('q'):
             break

client_socket.close()
cv2.destroyAllWindows()
