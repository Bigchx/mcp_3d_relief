import os
import numpy as np
from PIL import Image
import cv2
import asyncio
import json

async def generate_depth_map(image_path, detail_level=1.0, invert_depth=False):
    img = Image.open(image_path)
    
    base_size = 320 * detail_level
    width, height = img.size
    ratio = min(base_size/width, base_size/height)
    new_width, new_height = int(width * ratio), int(height * ratio)
    img = img.resize((new_width, new_height), Image.BICUBIC)
    
    img_array = np.array(img)
    
    if len(img_array.shape) == 3:
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]
        gray = 0.299 * r + 0.587 * g + 0.114 * b
    else:
        gray = img_array
    
    gray = np.power(gray/255.0, 1.5) * 255
    
    if invert_depth:
        gray = 255 - gray
    
    depth_map = gray.astype(np.uint8)
    
    depth_map = cv2.GaussianBlur(depth_map, (5, 5), 1.5)
    
    return depth_map

async def generate_stl(depth_map, output_path, model_width=50, model_thickness=5, base_thickness=2.0):
    height, width = depth_map.shape
    
    pixel_size = model_width / width
    
    with open(output_path, 'w') as f:
        f.write("solid relief_model\n")
        
        vertices = np.zeros((height, width))
        for y in range(height):
            for x in range(width):
                vertices[y, x] = (depth_map[y, x] / 255.0) * model_thickness
        
        for y in range(height - 1):
            for x in range(width - 1):
                y0 = (height - y - 1) * pixel_size
                y1 = (height - (y+1) - 1) * pixel_size
                x0 = x * pixel_size
                x1 = (x+1) * pixel_size
                
                write_facet(f, 
                    [x0, y0, -base_thickness],
                    [x1, y1, -base_thickness],
                    [x0, y1, -base_thickness]
                )
                write_facet(f,
                    [x0, y0, -base_thickness],
                    [x1, y0, -base_thickness],
                    [x1, y1, -base_thickness]
                )
        
        for y in range(height - 1):
            for x in range(width - 1):
                y0 = (height - y - 1) * pixel_size
                y1 = (height - (y+1) - 1) * pixel_size
                x0 = x * pixel_size
                x1 = (x+1) * pixel_size
                
                z00 = vertices[y, x]
                z01 = vertices[y+1, x]
                z10 = vertices[y, x+1]
                z11 = vertices[y+1, x+1]
                
                write_facet(f,
                    [x0, y0, z00],
                    [x1, y0, z10],
                    [x0, y1, z01]
                )
                write_facet(f,
                    [x1, y0, z10],
                    [x1, y1, z11],
                    [x0, y1, z01]
                )
        
        for x in range(width - 1):
            x0 = x * pixel_size
            x1 = (x+1) * pixel_size
            y0 = 0
            z0 = -base_thickness
            z1 = vertices[height-1, x]
            z2 = vertices[height-1, x+1]
            
            write_facet(f,
                [x0, y0, z0],
                [x1, y0, z0],
                [x0, y0, z1]
            )
            write_facet(f,
                [x1, y0, z0],
                [x1, y0, z2],
                [x0, y0, z1]
            )
        
        y0 = (height - 1) * pixel_size
        for x in range(width - 1):
            x0 = x * pixel_size
            x1 = (x+1) * pixel_size
            z0 = -base_thickness
            z1 = vertices[0, x]
            z2 = vertices[0, x+1]
            
            write_facet(f,
                [x0, y0, z0],
                [x0, y0, z1],
                [x1, y0, z0]
            )
            write_facet(f,
                [x1, y0, z0],
                [x1, y0, z2],
                [x0, y0, z1]
            )
        
        x0 = 0
        for y in range(height - 1):
            y0 = (height - y - 1) * pixel_size
            y1 = (height - (y+1) - 1) * pixel_size
            z0 = -base_thickness
            z1 = vertices[y, 0]
            z2 = vertices[y+1, 0]
            
            write_facet(f,
                [x0, y0, z0],
                [x0, y0, z1],
                [x0, y1, z0]
            )
            write_facet(f,
                [x0, y1, z0],
                [x0, y0, z1],
                [x0, y1, z2]
            )
        
        x0 = (width - 1) * pixel_size
        for y in range(height - 1):
            y0 = (height - y - 1) * pixel_size
            y1 = (height - (y+1) - 1) * pixel_size
            z0 = -base_thickness
            z1 = vertices[y, width-1]
            z2 = vertices[y+1, width-1]
            
            write_facet(f,
                [x0, y0, z0],
                [x0, y1, z0],
                [x0, y0, z1]
            )
            write_facet(f,
                [x0, y1, z0],
                [x0, y1, z2],
                [x0, y0, z1]
            )
        
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

async def main(args):
    print("Processing with args:", args)
    
    if 'input_image' not in args:
        return {
            "error": "No input image specified",
            "status": "failed"
        }
    
    detail_level = args.get('detail_level', 1.0)
    model_width = args.get('model_width', 50)
    model_thickness = args.get('model_thickness', 5)
    base_thickness = args.get('base_thickness', 2.0)
    output_dir = args.get('output_dir', 'output')
    skip_depth_conversion = args.get('skip_depth_conversion', True)
    invert_depth = args.get('invert_depth', False)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Check if input image exists
        if not os.path.exists(args['input_image']):
            return {
                "error": f"Input image not found: {args['input_image']}",
                "status": "failed"
            }
            
        original_filename = os.path.splitext(os.path.basename(args['input_image']))[0]
        
        print("Preparing image for 3D conversion...")
        if not skip_depth_conversion:
            img = cv2.imread(args['input_image'], cv2.IMREAD_GRAYSCALE)
            base_size = 320 * detail_level
            height, width = img.shape
            ratio = min(base_size/width, base_size/height)
            new_width, new_height = int(width * ratio), int(height * ratio)
            depth_map = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            depth_map = cv2.GaussianBlur(depth_map, (3, 3), 0.8)
            if invert_depth:
                depth_map = 255 - depth_map
            print("Using original image directly (skipping depth conversion)...")
        else:
            print("Generating depth map...")
            depth_map = await generate_depth_map(args['input_image'], detail_level, invert_depth)
        
        depth_map_path = os.path.join(output_dir, f"{original_filename}_depth_map.png")
        cv2.imwrite(depth_map_path, depth_map)
        
        print("Generating STL file...")
        stl_path = os.path.join(output_dir, f"{original_filename}.stl")
        await generate_stl(depth_map, stl_path, model_width, model_thickness, base_thickness)
        
        ret = {
            "depth_map_path": depth_map_path,
            "stl_path": stl_path,
            "status": "success"
        }
        
        print('result is: ', ret)
        return ret
        
    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        return {
            "error": error_message,
            "status": "failed"
        }

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) > 1:
        try:
            args = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            args = {
                'input_image': sys.argv[1],
                'test_1': 'default',
                'test_2': 'value'
            }
    else:
        args = {
            'input_image': 'example.jpg',
            'test_1': 'default',
            'test_2': 'value'
        }
    
    asyncio.run(main(args)) 