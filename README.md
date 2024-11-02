# Streaming Video Processing in S3 Storage

This repository provides a scalable solution for video streaming and processing using `S3` storage. Instead of downloading entire video files, which increases memory usage, this approach streams video data in small, manageable segments. The project leverages `PyAV` for video processing and `smart_open` for streaming to and from `S3`.

## Overview

Traditional video processing involves downloading a video, processing each frame, and then reassembling the video before uploading it back to storage. This can be memory-intensive and challenging to scale horizontally in environments like `Kubernetes`. By switching to a streaming approach, memory consumption remains constant, enabling better scalability and efficiency.

## Key Libraries

- [PyAV](https://github.com/PyAV-Org/PyAV) - Python bindings for `FFmpeg`, used for decoding, encoding, and processing video frames.
- [smart_open](https://github.com/piskvorky/smart_open) - Simplifies streaming data from `S3` using `boto3`.
- `click` - For running the processing script as a CLI utility.
- `numpy` - For image processing tasks, such as converting frames to grayscale.

## Setup

1. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2. Export required `AWS` credentials and region as environment variables:
    ```bash
    export AWS_ACCESS_KEY_ID=YOUR_KEY
    export AWS_SECRET_ACCESS_KEY=YOUR_SECRET
    export REGION_NAME=YOUR_REGION
    ```

## Running the Script

Use the following command to process a video from `S3`:
```bash
python main.py --s3_input_path s3://bucket/input_key.mp4 --s3_output_path s3://bucket/output_key.mp4
```

## Code Explanation

1. **S3 Connection**: Creates an `S3` client with `smart_open` for reading and writing video streams.
2. **Video Processing**: Converts each video frame to grayscale as a sample processing step. The script supports adding custom processing logic.
3. **Streaming Process**: Reads, processes, and writes video frames directly to `S3` without storing temporary files.

This solution avoids excessive memory usage and can be extended for different video processing tasks.
