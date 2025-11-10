# camera_socket

## Installation

You can install the necessary dependencies either by cloning the repository or by using `pip`.

### Option 1: Using `depthai-core` Repository

1.  **Create and activate a virtual environment:**
    * **Linux/macOS:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    * **Windows:**
        ```bash
        python3 -m venv venv
        venv\Scripts\activate
        ```

2.  **Clone the repository and install requirements:**
    ```bash
    git clone https://github.com/luxonis/depthai-core.git && cd depthai-core
    python3 -m venv venv
    source venv/bin/activate
    python3 examples/python/install_requirements.py
    ```

### Option 2: Using `pip`

```bash
pip install depthai --force-reinstall
````

-----

## Run Instructions


For **high-throughput systems**,  a thread si deployed for each camera.

### Simple JPG Encoded API

To set up a simple JPEG-encoded API and a test gnork server, run:

```bash
python API/create_and_publish.py
```

Access the streams in your browser at:

  * `LocalIP:8001/stream/0`
  * `LocalIP:8001/stream/1`
  * `LocalIP:8001/stream/x` (where `x` is the camera ID)

### Raw Data API

To push raw data, run the script with the `--raw` flag:

```bash
python API/create_and_publish.py --raw
```

> **Note:** Since this is raw data, you will need to read it using a custom decoder.

-----

## Sample Visualizer (For Raw Data)

Since raw data cannot be directly visualized, run this sample visualizer:

```bash
python API/rec_test.py
```

This will create viewing URLs:

  * `LocalIP:8002/view/all` | **All** camera feeds
  * `LocalIP:8002/view/x` | **Individual** camera feeds (where `x` = cam\_id)
