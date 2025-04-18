# Proto to Code Converter

A web-based tool that converts Protocol Buffers (proto) files to Python, Go, and Rust code. Built with FastAPI and deployed on Modal.

## Features

- Convert proto files to multiple languages:
  - Python
  - Go
  - Rust (using μpb implementation)
- Copy to clipboard functionality
- Version information display

## Prerequisites

- Python 3.10+
- protoc compiler
- For Go support: Go compiler
- For Rust support: Rust and Cargo

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/proto-to-python-script.git
cd proto-to-python-script
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally

1. Start the FastAPI server:
```bash
uvicorn src.main:fastapi_app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Deployment

The application is configured for deployment on Modal. To deploy:

1. Install Modal CLI:
```bash
pip install modal
```

2. Deploy the application:
```bash
modal deploy
```

## Usage

1. Enter your proto file content in the text area
2. Select the target language (Python, Go, or Rust)
3. For Go, enter the package path
4. Click "Convert" to generate the code
5. Copy the generated code using the copy button

## Example

Input proto:
```protobuf
syntax = "proto2";

message AirQualityReading {
    optional int32 temp = 1;
    optional int64 humidity = 2;
    optional int64 timestamp = 3;
}

message AirQuality {
    optional string device_name = 1;
    repeated AirQualityReading readings = 2;
    repeated string tags = 3;
}
```
