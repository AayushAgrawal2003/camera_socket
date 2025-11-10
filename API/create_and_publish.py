import cv2
import depthai as dai
from flask import Flask, Response, request
from pyngrok import ngrok
import threading
import argparse

# Store latest frame for each camera
latest_frames = {}
latest_raw = {}  # Store raw bytes if --raw

# Keep pipeline references alive
pipelines = []

parser = argparse.ArgumentParser()
parser.add_argument("--raw", action="store_true", help="Send raw uncompressed frames")
args = parser.parse_args()

def createPipeline(pipeline):
    camRgb = pipeline.create(dai.node.Camera).build()
    output = camRgb.requestOutput((640, 400)).createOutputQueue()
    return pipeline, output

def camera_thread(deviceIndex, stream):
    global latest_frames, latest_raw
    while True:
        try:
            videoIn = stream.get()
            frame = videoIn.getCvFrame()  # BGR numpy
            latest_frames[deviceIndex] = frame

            if args.raw:
                h, w, c = frame.shape
                data = frame.tobytes()
                latest_raw[deviceIndex] = {
                    "h": h, "w": w, "c": c, "data": data
                }

        except dai.MessageQueue.Closed:
            print(f"Queue closed for camera {deviceIndex}, exiting thread.")
            break

# --- Flask MJPEG / Raw Stream API ---
app = Flask(__name__)

@app.route('/stream/<int:cam_id>')
def stream(cam_id):
    def generate_jpeg():
        while True:
            if cam_id in latest_frames and latest_frames[cam_id] is not None:
                ret, jpeg = cv2.imencode('.jpg', latest_frames[cam_id])
                if ret:
                    yield (b"--frame\r\n"
                           b"Content-Type: image/jpeg\r\n\r\n" +
                           jpeg.tobytes() + b"\r\n\r\n")

    def generate_raw():
        while True:
            if cam_id in latest_raw:
                raw_frame = latest_raw[cam_id]
                frame_bytes = raw_frame["data"]
                h, w, c = raw_frame["h"], raw_frame["w"], raw_frame["c"]

                # Send as binary block
                yield (h.to_bytes(4, 'big') +
                       w.to_bytes(4, 'big') +
                       c.to_bytes(4, 'big') +
                       frame_bytes)

    if args.raw:
        return Response(generate_raw(), mimetype='application/octet-stream')
    else:
        return Response(generate_jpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')


def start_cameras():
    devices = dai.Device.getAllAvailableDevices()
    print("=== Found devices: ", devices)
    queues = []

    for deviceIndex, deviceInfo in enumerate(devices):
        pipeline = dai.Pipeline()
        pipeline, output = createPipeline(pipeline)
        pipeline.start()
        pipelines.append(pipeline)
        queues.append((deviceIndex, output))

    for deviceIndex, stream in queues:
        t = threading.Thread(target=camera_thread, args=(deviceIndex, stream), daemon=True)
        t.start()
        print(f"Started camera thread as cam_id {deviceIndex}")


if __name__ == "__main__":
    start_cameras()
    print("Starting local API on http://localhost:8001/stream/<cam_id>")
    public_url = ngrok.connect(8001, "http")
    print("PUBLIC STREAM URL (replace <cam_id> with 0,1,...):", public_url)

    app.run(host="0.0.0.0", port=8001, threaded=True)
