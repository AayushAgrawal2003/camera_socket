# camera_socket

Current Support Single Camera raw and compressed

## Installation
git clone https://github.com/luxonis/depthai-core.git && cd depthai-core
python3 -m venv venv
source venv/bin/activate
python3 examples/python/install_requirements.py

---- OR ----

pip install depthai --force-reinstall



## Run Instructions Single Camera
python test_rec.py \
python sender.py --raw / For Uncompressed \
python sender.py / For JPEG Compression

## Run Multi Camera 
python test_rec_multi.py \
python multi.py --raw / For Uncompressed \
python multi.py / For JPEG Compression 

## Creating an API
To create a simple JPG encoded API you can just run 
python API/create_and_publish.py
This should also run a gnork server for test 
You can now view data simply in the browser 
 
"LocalIP:8001/stream/0",
"LocalIP:8001/stream/1",
"LocalIP:8001/stream/x",
x = cam_id

If you want to push through raw data
python API/create_and_publish.py --raw
Since its raw data you will need to read using a custom decoder: 
python API/rec_test.py
This should create 5 URLs:
LocalIP:8002/view/all | All camera feeds
LocalIP:8002/view/x   | x = cam_id

