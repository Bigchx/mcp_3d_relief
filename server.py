import os
import uuid
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil
from mcp_3d_relief import main
import asyncio

app = FastAPI(title="STL 3D RELIEF MCP Server")

os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)

app.mount("/files", StaticFiles(directory="output"), name="files")

@app.post("/convert")
async def convert_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model_width: float = Form(50.0),
    model_thickness: float = Form(5.0),
    base_thickness: float = Form(2.0),
    skip_depth_conversion: bool = Form(True),
    invert_depth: bool = Form(False)
):
    original_filename = file.filename
    file_extension = os.path.splitext(original_filename)[1]
    
    file_id = str(uuid.uuid4())
    file_location = f"uploads/{file_id}{file_extension}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    args = {
        'input_image': file_location,
        'model_width': model_width,
        'model_thickness': model_thickness,
        'base_thickness': base_thickness,
        'output_dir': 'output',
        'skip_depth_conversion': skip_depth_conversion,
        'invert_depth': invert_depth
    }
    
    result = await main(args)
    
    if result.get("status") == "success":
        depth_map_filename = os.path.basename(result["depth_map_path"])
        stl_filename = os.path.basename(result["stl_path"])
        
        result["depth_map_url"] = f"/files/{depth_map_filename}"
        result["stl_url"] = f"/files/{stl_filename}"
        
        background_tasks.add_task(cleanup_upload, file_location)
    
    return result

def cleanup_upload(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

@app.get("/")
async def root():
    return {"message": "Welcome to STL 3D RELIEF MCP SERVER", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True) 