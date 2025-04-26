# MCP STL 3D 浮雕生成器

本项目提供一个 MCP server，能够将 2D 图像转换为 STL 格式的 3D 浮雕模型，适用于 3D 打印或渲染。

## 功能特点

- 将任何图像转换为 3D 浮雕模型
- 可控制模型尺寸（宽度、厚度）
- 可为 3D 模型添加可选底座
- 可反转深度以获得不同的浮雕效果
- 快速处理，立即提供下载链接

## 安装

### 前提条件

- Python 3.10+
- [uv](https://docs.astral.sh/uv/#installation)

### 选项 1：本地安装

1. 克隆仓库：

```bash
git clone https://github.com/bigchx/mcp_3d_relief.git
cd mcp_3d_relief
```

2. 安装依赖：

```bash
uv pip sync requirements.txt
```

3. 运行/调试服务器：

```bash
mcp run server.py
mcp dev server.py
```

## 使用方法

### JSON 配置

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

### MCP 工具参数

- `image_path`：要转换的图像本地路径或 URL
- `model_width`：3D 模型的宽度（毫米，默认：50.0）
- `model_thickness`：3D 模型的最大厚度/高度（毫米，默认：5.0）
- `base_thickness`：底座厚度（毫米，默认：2.0）
- `skip_depth`：是否直接使用图像或生成深度图（默认：true）
- `invert_depth`：是否反转浮雕（明亮区域变低而不是高，默认：false）
- `detail_level`：控制处理图像的分辨率（默认：1.0）。当 detail_level = 1.0 时，图像以 320px 分辨率处理，生成的 STL 文件通常在 100MB 以内。较高的值可以提高细节质量，但会显著增加处理时间和 STL 文件大小。例如，将 detail_level 值加倍可能会使文件大小增加 4 倍或更多，请谨慎使用。

### 响应

MCP 工具返回的 JSON 响应包含：

```json
{
  "status": "success",
  "depth_map_path": "path/to/yourimage_depth_map.png",
  "stl_path": "path/to/yourimage.stl"
}
```

大语言模型可通过提供的 URL 访问生成的文件。

### 命令行

您也可以直接从命令行使用脚本：

```bash
python3 relief.py path/to/your/image.jpg
```

### 外部深度图生成

为获得更高质量的深度图，您可以使用外部深度图生成服务，如 [Depth-Anything-V2](https://huggingface.co/spaces/depth-anything/Depth-Anything-V2)。该服务可以生成更准确的深度图，然后您可以将其用于本项目：

1. 访问 [https://huggingface.co/spaces/depth-anything/Depth-Anything-V2](https://huggingface.co/spaces/depth-anything/Depth-Anything-V2)
2. 上传您的图像以生成深度图
3. 下载生成的深度图
4. 将此深度图与我们的转换器一起使用，设置 `skip_depth=false`

这种方法可以提供更好的 3D 浮雕模型，特别是对于复杂图像。

## 工作原理

1. 处理图像创建深度图（较暗像素 = 较低，较亮像素 = 较高）
2. 将深度图转换为带有三角形面的 3D 网格
3. 在模型底部添加底座
4. 将模型保存为 STL 文件

## 合作伙伴

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
