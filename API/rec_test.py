import requests
import cv2
import numpy as np
from flask import Flask, Response

# Replace with your actual raw stream URLs
RAW_URLS = [
    "http://192.168.1.213:8001/stream/0",
    "http://192.168.1.213:8001/stream/1",
    "http://192.168.1.213:8001/stream/2",
    "http://192.168.1.213:8001/stream/3"
]

app = Flask(__name__)

def fetch_raw_frames(url):
    """Generator that yields frames from a raw camera URL"""
    stream = requests.get(url, stream=True)
    buffer = b""
    for chunk in stream.iter_content(chunk_size=4096):
        if chunk:
            buffer += chunk
            while len(buffer) >= 12:
                h = int.from_bytes(buffer[0:4], 'big')
                w = int.from_bytes(buffer[4:8], 'big')
                c = int.from_bytes(buffer[8:12], 'big')
                frame_len = h * w * c
                if len(buffer) < 12 + frame_len:
                    break
                frame_data = buffer[12:12+frame_len]
                frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((h, w, c))
                buffer = buffer[12+frame_len:]
                yield frame

# Create generators for all 4 cameras
generators = [fetch_raw_frames(url) for url in RAW_URLS]

def generate_single(cam_id):
    """Yield MJPEG for a single camera"""
    gen = generators[cam_id]
    while True:
        try:
            frame = next(gen)
            # Raw bits passed until here beyond this point whatever encoded is needed can be used.
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" +
                       jpeg.tobytes() + b"\r\n\r\n")
        except StopIteration:
            continue

def generate_all():
    """Yield MJPEG of all 4 cameras in 2x2 grid"""
    while True:
        frames = []
        for gen in generators:
            try:
                frame = next(gen)
                frames.append(frame)
            except StopIteration:
                # Use black placeholder if no frame
                frames.append(np.zeros((400, 640, 3), dtype=np.uint8))

        # Resize frames to same size
        target_h, target_w = 400, 640
        frames = [cv2.resize(f, (target_w, target_h)) for f in frames]

        # Combine into 2x2 grid
        top = cv2.hconcat([frames[0], frames[1]])
        bottom = cv2.hconcat([frames[2], frames[3]])
        combined = cv2.vconcat([top, bottom])

        ret, jpeg = cv2.imencode('.jpg', combined)
        if ret:
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" +
                   jpeg.tobytes() + b"\r\n\r\n")

# --- Flask Endpoints ---
for i in range(4):
    app.add_url_rule(f'/view/{i}', f'view_{i}', lambda i=i: Response(generate_single(i),
                                                                   mimetype='multipart/x-mixed-replace; boundary=frame'))

app.add_url_rule('/view/all', 'view_all', lambda: Response(generate_all(),
                                                          mimetype='multipart/x-mixed-replace; boundary=frame'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002, threaded=True)
