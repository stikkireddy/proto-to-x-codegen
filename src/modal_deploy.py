import modal
from pathlib import Path

app = modal.App("proto-to-python-converter")

# Create a Modal image with all required dependencies
image = modal.Image.debian_slim(python_version="3.10")\
    .pip_install_from_requirements("../requirements.txt")\
    .apt_install("protobuf-compiler", "git", "curl")\
    .run_commands(
        # Install Go
        "curl -OL https://golang.org/dl/go1.23.8.linux-amd64.tar.gz && "
        "tar -C /usr/local -xzf go1.23.8.linux-amd64.tar.gz && "
        "rm go1.23.8.linux-amd64.tar.gz && "
        "mkdir -p /root/go && "
        "export GOPATH=/root/go && "
        "export PATH=/usr/local/go/bin:$PATH && "
        "export GO111MODULE=on && "
        "go install google.golang.org/protobuf/cmd/protoc-gen-go@latest && "
        # Install Rust and protobuf-rust
        "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && "
        "/root/.cargo/bin/cargo install protobuf-codegen"
    )\
    .env({
        "GOPATH": "/root/go",
        "GO111MODULE": "on",
    })

# Add the local files to the image
image = image.add_local_dir(
    Path(__file__).parent,
    remote_path="/root"
)

@app.function(
    image=image,
    timeout=600,
    scaledown_window=5,
)
@modal.concurrent(max_inputs=30)
@modal.asgi_app()
def web():
    import os
    os.environ["PATH"] = "/root/go/bin:/root/.cargo/bin:" + os.environ["PATH"]
    from main import fastapi_app
    return fastapi_app 