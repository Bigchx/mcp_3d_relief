import asyncio
import io
import logging
import os
import random
import string
from traceback import print_exc

import cv2
import numpy as np
from aiohttp import ClientSession
from PIL import Image

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
file_handler = logging.FileHandler("relief.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


async def generate_depth_map(img, detail_level=1.0, invert_depth=False):
    base_size = 320 * detail_level
    width, height = img.size
    ratio = min(base_size / width, base_size / height)
    new_width, new_height = int(width * ratio), int(height * ratio)
    img = img.resize((new_width, new_height), Image.BICUBIC)

    img_array = np.array(img)

    if len(img_array.shape) == 3:
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        gray = 0.299 * r + 0.587 * g + 0.114 * b
    else:
        gray = img_array

    gray = np.power(gray / 255.0, 1.5) * 255

    if invert_depth:
        gray = 255 - gray

    depth_map = gray.astype(np.uint8)

    depth_map = cv2.GaussianBlur(depth_map, (5, 5), 1.5)

    return depth_map


async def generate_stl(
    depth_map, output_path, model_width=50, model_thickness=5, base_thickness=2.0
):
    height, width = depth_map.shape

    pixel_size = model_width / width

    with open(output_path, "w") as f:
        f.write("solid relief_model\n")

        vertices = np.zeros((height, width))
        for y in range(height):
            for x in range(width):
                vertices[y, x] = (depth_map[y, x] / 255.0) * model_thickness

        for y in range(height - 1):
            for x in range(width - 1):
                y0 = (height - y - 1) * pixel_size
                y1 = (height - (y + 1) - 1) * pixel_size
                x0 = x * pixel_size
                x1 = (x + 1) * pixel_size

                write_facet(
                    f,
                    [x0, y0, -base_thickness],
                    [x1, y1, -base_thickness],
                    [x0, y1, -base_thickness],
                )
                write_facet(
                    f,
                    [x0, y0, -base_thickness],
                    [x1, y0, -base_thickness],
                    [x1, y1, -base_thickness],
                )

        for y in range(height - 1):
            for x in range(width - 1):
                y0 = (height - y - 1) * pixel_size
                y1 = (height - (y + 1) - 1) * pixel_size
                x0 = x * pixel_size
                x1 = (x + 1) * pixel_size

                z00 = vertices[y, x]
                z01 = vertices[y + 1, x]
                z10 = vertices[y, x + 1]
                z11 = vertices[y + 1, x + 1]

                write_facet(f, [x0, y0, z00], [x1, y0, z10], [x0, y1, z01])
                write_facet(f, [x1, y0, z10], [x1, y1, z11], [x0, y1, z01])

        for x in range(width - 1):
            x0 = x * pixel_size
            x1 = (x + 1) * pixel_size
            y0 = 0
            z0 = -base_thickness
            z1 = vertices[height - 1, x]
            z2 = vertices[height - 1, x + 1]

            write_facet(f, [x0, y0, z0], [x1, y0, z0], [x0, y0, z1])
            write_facet(f, [x1, y0, z0], [x1, y0, z2], [x0, y0, z1])

        y0 = (height - 1) * pixel_size
        for x in range(width - 1):
            x0 = x * pixel_size
            x1 = (x + 1) * pixel_size
            z0 = -base_thickness
            z1 = vertices[0, x]
            z2 = vertices[0, x + 1]

            write_facet(f, [x0, y0, z0], [x0, y0, z1], [x1, y0, z0])
            write_facet(f, [x1, y0, z0], [x1, y0, z2], [x0, y0, z1])

        x0 = 0
        for y in range(height - 1):
            y0 = (height - y - 1) * pixel_size
            y1 = (height - (y + 1) - 1) * pixel_size
            z0 = -base_thickness
            z1 = vertices[y, 0]
            z2 = vertices[y + 1, 0]

            write_facet(f, [x0, y0, z0], [x0, y0, z1], [x0, y1, z0])
            write_facet(f, [x0, y1, z0], [x0, y0, z1], [x0, y1, z2])

        x0 = (width - 1) * pixel_size
        for y in range(height - 1):
            y0 = (height - y - 1) * pixel_size
            y1 = (height - (y + 1) - 1) * pixel_size
            z0 = -base_thickness
            z1 = vertices[y, width - 1]
            z2 = vertices[y + 1, width - 1]

            write_facet(f, [x0, y0, z0], [x0, y1, z0], [x0, y0, z1])
            write_facet(f, [x0, y1, z0], [x0, y1, z2], [x0, y0, z1])

        f.write("endsolid relief_model\n")

    return output_path


def write_facet(file, v1, v2, v3):
    a = np.array(v2) - np.array(v1)
    b = np.array(v3) - np.array(v1)
    normal = np.cross(a, b)
    if np.linalg.norm(normal) > 0:
        normal = normal / np.linalg.norm(normal)

    file.write(f"  facet normal {normal[0]} {normal[1]} {normal[2]}\n")
    file.write("    outer loop\n")
    file.write(f"      vertex {v1[0]} {v1[1]} {v1[2]}\n")
    file.write(f"      vertex {v2[0]} {v2[1]} {v2[2]}\n")
    file.write(f"      vertex {v3[0]} {v3[1]} {v3[2]}\n")
    file.write("    endloop\n")
    file.write("  endfacet\n")


async def relief(
    input_image_path: str = None,
    input_image: Image.Image = None,
    detail_level: float = 1.0,
    model_width: float = 50.0,
    model_thickness: float = 5.0,
    base_thickness: float = 2.0,
    output_dir: str = "./output",
    skip_depth: bool = False,
    invert_depth: bool = False,
):
    logger.info("Processing image...")

    if input_image_path is not None:
        if input_image_path.startswith("http://") or input_image_path.startswith(
            "https://"
        ):
            async with ClientSession() as session:
                async with session.get(input_image_path) as response:
                    if response.status != 200:
                        return {
                            "error": f"Failed to download image from URL: {input_image_path}",
                            "status": "failed",
                        }
                    img_data = await response.read()
                    input_image = Image.open(io.BytesIO(img_data))
        elif os.path.isfile(input_image_path):
            if not os.path.exists(input_image_path):
                return {
                    "error": f"Input image not found: {input_image_path}",
                    "status": "failed",
                }
            input_image = Image.open(input_image_path)
        else:
            return {
                "error": f"Invalid input image path: {input_image_path}",
                "status": "failed",
            }
    elif input_image is None:
        return {"error": "No input image specified", "status": "failed"}

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        original_filename = "".join(
            random.choices(string.ascii_letters + string.digits, k=10)
        )

        logger.info("Preparing image for 3D conversion...")
        if not skip_depth:
            img = np.array(input_image.convert("L"))
            base_size = 320 * detail_level
            height, width = img.shape
            ratio = min(base_size / width, base_size / height)
            new_width, new_height = int(width * ratio), int(height * ratio)
            depth_map = cv2.resize(
                img, (new_width, new_height), interpolation=cv2.INTER_CUBIC
            )
            depth_map = cv2.GaussianBlur(depth_map, (3, 3), 0.8)
            if invert_depth:
                depth_map = 255 - depth_map
            logger.info("Using original image directly (skipping depth conversion)...")
        else:
            logger.info("Generating depth map...")
            depth_map = await generate_depth_map(
                input_image, detail_level, invert_depth
            )

        depth_map_name = f"{original_filename}_depth_map.png"
        depth_map_path = os.path.join(output_dir, depth_map_name)
        cv2.imwrite(depth_map_path, depth_map)

        logger.info("Generating STL file...")
        stl_name = f"{original_filename}.stl"
        stl_path = os.path.join(output_dir, stl_name)
        await generate_stl(
            depth_map, stl_path, model_width, model_thickness, base_thickness
        )

        ret = {
            "depth_map_path": os.path.abspath(depth_map_path),
            "stl_path": os.path.abspath(stl_path),
            "status": "success",
        }

        logger.info(f"result is: {ret}")
        return ret

    except Exception as e:
        error_message = repr(e)
        print_exc()
        logger.warning(f"Error processing image: {error_message}")
        return {"error": error_message, "status": "failed"}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate STL from image")
    parser.add_argument(
        "input_image_path",
        type=str,
        help="Path to the input image file or URL",
    )
    parser.add_argument(
        "--detail_level",
        type=float,
        default=1.0,
        help="Detail level for depth map generation",
    )
    parser.add_argument(
        "--model_width",
        type=float,
        default=50.0,
        help="Width of the 3D model in mm",
    )
    parser.add_argument(
        "--model_thickness",
        type=float,
        default=5.0,
        help="Thickness of the 3D model in mm",
    )
    parser.add_argument(
        "--base_thickness",
        type=float,
        default=2.0,
        help="Base thickness of the 3D model in mm",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Directory to save the output STL file",
    )
    parser.add_argument(
        "--skip_depth",
        action="store_true",
        help="Skip depth map generation and use the original image directly",
    )
    parser.add_argument(
        "--invert_depth",
        action="store_true",
        help="Invert the depth map",
    )
    args = parser.parse_args()
    asyncio.run(
        relief(
            input_image_path=args.input_image_path,
            detail_level=args.detail_level,
            model_width=args.model_width,
            model_thickness=args.model_thickness,
            base_thickness=args.base_thickness,
            output_dir=args.output_dir,
            skip_depth=args.skip_depth,
            invert_depth=args.invert_depth,
        )
    )
