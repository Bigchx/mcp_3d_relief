# STL 3D Relief Generator

This project provides a web service that converts 2D images into 3D relief models in STL format, suitable for 3D printing or rendering.

## Features

- Convert any image to a 3D relief model
- Control model dimensions (width, thickness)
- Add optional base to the 3D model
- Invert depth for different relief effects
- Fast processing with immediate download links
- Simple REST API interface

## Installation

### Prerequisites

- Python 3.9+
- Docker (optional)

### Option 1: Local Installation

1. Clone the repository:
```
git clone https://github.com/bigchx/mcp_3d_relief.git
cd mcp_3d_relief
```

2. Install dependencies:
```
pip install -r requirements.txt
```

3. Run the server:
```
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Option 2: Docker

1. Build the Docker image:
```
docker build -t mcp_3d_relief .
```

2. Run the container:
```
docker run -p 8000:8000 mcp_3d_relief
```

## Usage

### Web API

Once the server is running, access the API at http://localhost:8000.

#### Convert an image to STL

Send a POST request to `/convert` with the following form data:

- `file`: The image file to convert
- `model_width`: Width of the 3D model in mm (default: 50.0)
- `model_thickness`: Maximum thickness/height of the 3D model in mm (default: 5.0)
- `base_thickness`: Thickness of the base in mm (default: 2.0)
- `skip_depth_conversion`: Whether to use the image directly or generate a depth map (default: true)
- `invert_depth`: Invert the relief (bright areas become low instead of high) (default: false)
- `detail_level`: Controls the resolution of the processed image (default: 1.0). At detail_level = 1.0, the image is processed at 320px resolution, producing an STL file typically under 100MB. Higher values improve detail quality but significantly increase both processing time and STL file size. For example, doubling the detail_level can increase file size by 4x or more. Use with caution.

Example using curl:
```
curl -X POST http://localhost:8000/convert \
  -F "file=@path/to/your/image.jpg" \
  -F "model_width=50" \
  -F "model_thickness=5" \
  -F "base_thickness=2" \
  -F "skip_depth_conversion=true" \
  -F "invert_depth=false" \
  -F "detail_level=1.0"
```

### Response

The API returns a JSON response with:

```json
{
  "status": "success",
  "depth_map_path": "output/yourimage_depth_map.png",
  "stl_path": "output/yourimage.stl",
  "depth_map_url": "/files/yourimage_depth_map.png",
  "stl_url": "/files/yourimage.stl"
}
```

You can access the generated files directly via the provided URLs.

### Command Line

You can also use the script directly from the command line:

```
python mcp_3d_relief.py '{"input_image": "example.jpg", "model_width": 50, "model_thickness": 5}'
```

### External Depth Map Generation

For higher quality depth maps, you can use external depth map generation services like [Depth-Anything-V2](https://huggingface.co/spaces/depth-anything/Depth-Anything-V2). This service can generate more accurate depth maps that you can then use with this project:

1. Visit [https://huggingface.co/spaces/depth-anything/Depth-Anything-V2](https://huggingface.co/spaces/depth-anything/Depth-Anything-V2)
2. Upload your image to generate a depth map
3. Download the generated depth map
4. Use this depth map with our converter by setting `skip_depth_conversion=false`

This approach can provide better 3D relief models, especially for complex images.

## How It Works

1. The image is processed to create a depth map (darker pixels = lower, brighter pixels = higher)
2. The depth map is converted to a 3D mesh with triangular facets
3. A base is added to the bottom of the model
4. The model is saved as an STL file

## License

This project is licensed under the MIT License - see the LICENSE file for details. 