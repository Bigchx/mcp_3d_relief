# MCP STL 3D Relief Generator

<div align="center">

[中文](README_CN.md)
·
[Introduction to MCP](https://modelcontextprotocol.io/introduction)
·
[Wiki](https://deepwiki.com/Bigchx/mcp_3d_relief)

</div>

This project provides a MCP server that converts 2D images into 3D relief models in STL format, suitable for 3D printing or rendering.

## Features

- Convert any image to a 3D relief model
- Control model dimensions (width, thickness)
- Add optional base to the 3D model
- Invert depth for different relief effects
- Fast processing with immediate download links

## Installation

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/#installation)

### Option 1: Local Installation

1. Clone the repository:

```bash
git clone https://github.com/bigchx/mcp_3d_relief.git
cd mcp_3d_relief
```

2. Install dependencies:

```bash
uv pip sync requirements.txt
```

3. Run/Inspect the server:

```bash
mcp run server.py
mcp dev server.py
```

## Usage

### JSON Configuration

```json
{
  "mcpServers": {
    "mcp_3d_relief": {
      "command": "uv",
      "args": ["--directory", "{fill_in_your_path_here}", "run", "server.py"]
    }
  }
}
```

### MCP Tool Parameters

- `image_path`: Local path or web URL to the input image file
- `model_width`: Width of the 3D model in mm (default: 50.0)
- `model_thickness`: Maximum thickness/height of the 3D model in mm (default: 5.0)
- `base_thickness`: Thickness of the base in mm (default: 2.0)
- `skip_depth`: Whether to use the image directly or generate a depth map (default: true)
- `invert_depth`: Invert the relief (bright areas become low instead of high) (default: false)
- `detail_level`: Controls the resolution of the processed image (default: 1.0). At detail_level = 1.0, the image is processed at 320px resolution, producing an STL file typically under 100MB. Higher values improve detail quality but significantly increase both processing time and STL file size. For example, doubling the detail_level can increase file size by 4x or more. Use with caution.

### Response

The MCP Tool returns a JSON response with:

```json
{
  "status": "success",
  "depth_map_path": "path/to/yourimage_depth_map.png",
  "stl_path": "path/to/yourimage.stl"
}
```

Where LLMs can access the generated files from this MCP server, using the provided URLs.

### Command Line

You can also use the script directly from the command line to generate a relief model from an image:

```bash
python3 relief.py path/to/your/image.jpg
```

### External Depth Map Generation

For higher quality depth maps, you can use external depth map generation services like [Depth-Anything-V2](https://huggingface.co/spaces/depth-anything/Depth-Anything-V2). This service can generate more accurate depth maps that you can then use with this project:

1. Visit [https://huggingface.co/spaces/depth-anything/Depth-Anything-V2](https://huggingface.co/spaces/depth-anything/Depth-Anything-V2)
2. Upload your image to generate a depth map
3. Download the generated depth map
4. Use this depth map with our converter by setting `skip_depth=false`

This approach can provide better 3D relief models, especially for complex images.

## How It Works

1. The image is processed to create a depth map (darker pixels = lower, brighter pixels = higher)
2. The depth map is converted to a 3D mesh with triangular facets
3. A base is added to the bottom of the model
4. The model is saved as an STL file

## Our partners

<div style="display: flex; justify-content: center; align-items: center; gap: 20px; margin: 30px 0;">
  <div style="flex: 1; text-align: center; padding: 15px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: all 0.2s ease-in-out; max-width: 300px; hover:transform: translateY(-5px); hover:box-shadow: 0 6px 16px rgba(0,0,0,0.15);">
    <a href="https://www.voxeldance.com/" style="display: block; height: 100%;">
      <img src="images/voxeldance.png" alt="voxeldance" style="max-width: 100%; height: auto; object-fit: contain; transition: opacity 0.2s ease-in-out;">
    </a>
  </div>
  <div style="flex: 1; text-align: center; padding: 15px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: all 0.2s ease-in-out; max-width: 300px; hover:transform: translateY(-5px); hover:box-shadow: 0 6px 16px rgba(0,0,0,0.15);">
    <a href="https://www.3dzyk.cn/" style="display: block; height: 100%;">
      <img src="images/3dzyk.png" alt="3dzyk" style="max-width: 100%; height: auto; object-fit: contain; transition: opacity 0.2s ease-in-out;">
    </a>
  </div>
</div>
