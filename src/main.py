import os
import tempfile
import subprocess
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import pkg_resources

fastapi_app = FastAPI()

# Create templates directory and mount static files
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_library_versions():
    versions = {
        'python': {},
        'protoc': {}
    }
    try:
        # Python versions
        versions['python']['grpcio-tools'] = pkg_resources.get_distribution('grpcio-tools').version
        versions['python']['grpcio'] = pkg_resources.get_distribution('grpcio').version
        versions['python']['protobuf'] = pkg_resources.get_distribution('protobuf').version
        
        # Get protoc version
        try:
            result = subprocess.run(['protoc', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                versions['protoc']['version'] = result.stdout.strip()
            else:
                versions['protoc']['version'] = 'Not available'
        except Exception:
            versions['protoc']['version'] = 'Not available'
            
    except Exception as e:
        versions['error'] = str(e)
    return versions

@fastapi_app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    versions = get_library_versions()
    return templates.TemplateResponse("index.html", {"request": request, "versions": versions})

@fastapi_app.post("/upload/")
async def upload_proto(file: UploadFile = File(...), language: str = Form("python"), go_package: str = Form(None)):
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the uploaded file
        temp_proto_path = os.path.join(temp_dir, file.filename)
        with open(temp_proto_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        try:
            # Get the directory containing the proto file
            proto_dir = os.path.dirname(temp_proto_path)
            proto_filename = os.path.basename(temp_proto_path)
            
            if language == "python":
                # Generate Python file
                command = [
                    "python3", "-m", "grpc_tools.protoc",
                    f"-I{proto_dir}",
                    f"--python_out={proto_dir}",
                    proto_filename
                ]
                subprocess.run(command, cwd=proto_dir, check=True)
                
                # Read the generated Python file
                output_filename = file.filename.replace(".proto", "_pb2.py")
                output_path = os.path.join(proto_dir, output_filename)
                
            elif language == "go":
                if not go_package:
                    return {
                        "status": "error",
                        "message": "Go package path is required for Go code generation",
                        "versions": get_library_versions()
                    }
                
                # Generate Go file
                command = [
                    "protoc",
                    f"-I{proto_dir}",
                    f"--go_out={proto_dir}",
                    f"--go_opt=paths=source_relative",
                    f"--go_opt=M{proto_filename}={go_package}",
                    proto_filename
                ]
                subprocess.run(command, cwd=proto_dir, check=True)
                
                # Read the generated Go file
                output_filename = file.filename.replace(".proto", ".pb.go")
                output_path = os.path.join(proto_dir, output_filename)

            elif language == "rust":
                # Generate Rust file
                command = [
                    "protoc",
                    f"-I{proto_dir}",
                    f"--rs_out={proto_dir}",
                    proto_filename
                ]
                subprocess.run(command, cwd=proto_dir, check=True)
                
                # Read the generated Rust file
                output_filename = file.filename.replace(".proto", ".rs")
                output_path = os.path.join(proto_dir, output_filename)
            
            with open(output_path, "r") as f:
                output_content = f.read()
            
            versions = get_library_versions()
            
            return {
                "status": "success",
                "generated_code": output_content,
                "filename": output_filename,
                "versions": versions,
                "command": " ".join(command)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "message": f"Error generating {language} file: {str(e)}",
                "versions": get_library_versions()
            } 
        
 