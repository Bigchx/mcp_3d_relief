import os
from typing import Annotated

from fastapi import FastAPI, Form
from fastmcp import FastMCP
from pydantic import Field

from relief import relief

app = FastAPI(title="STL 3D RELIEF MCP Server")

os.makedirs("uploads", exist_ok=True)
os.makedirs("output", exist_ok=True)


@app.post("/convert")
async def convert_image(
    image_path: Annotated[
        str,
        Field(
            description="2 possible options on this paramater: "
            "1. Path to the image file. (Save the image locally and return the path to the file. Delete the file after processing this tool.)"
            "2. Online image URL. (Provide the original image URL, or upload the image to a public server and provide the URL.)",
        ),
    ],
    model_width: float = Form(50.0),
    model_thickness: float = Form(5.0),
    base_thickness: float = Form(2.0),
    skip_depth: bool = Form(False),
    invert_depth: bool = Form(False),
    detail_level: float = Form(1.0),
) -> dict:
    """
    Convert an image to a 3D relief STL file.

    Args:
        image_path (str): Local path or web URL to the input image file.
        model_width (float): Width of the model in mm.
        model_thickness (float): Thickness of the model in mm.
        base_thickness (float): Thickness of the base in mm.
        skip_depth (bool): Whether to skip depth conversion.
        invert_depth (bool): Whether to invert depth.
        detail_level (float): Detail level for depth map generation.
    """
    result = await relief(
        input_image_path=image_path,
        model_width=model_width,
        model_thickness=model_thickness,
        base_thickness=base_thickness,
        output_dir="output",
        skip_depth=skip_depth,
        invert_depth=invert_depth,
        detail_level=detail_level,
    )
    return result


mcp = FastMCP.from_fastapi(app, "mcp_3d_relief")

if __name__ == "__main__":
    mcp.run(transport="stdio")
