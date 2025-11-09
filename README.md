# camera_socket

Current Support Single Camera raw and compressed

Installation:
git clone https://github.com/luxonis/depthai-core.git && cd depthai-core
python3 -m venv venv
source venv/bin/activate
python3 examples/python/install_requirements.py

---- OR ----

pip install depthai --force-reinstall


Run Instructions
python test_rec.py 
python sender.py --raw / For Uncompressed
python sender.py / For JPEG Compression