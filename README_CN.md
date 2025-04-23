# STL 3D 浮雕生成器

本项目提供一个网络服务，能够将 2D 图像转换为 STL 格式的 3D 浮雕模型，适用于 3D 打印或渲染。

## 功能特点

- 将任何图像转换为 3D 浮雕模型
- 可控制模型尺寸（宽度、厚度）
- 可为 3D 模型添加可选底座
- 可反转深度以获得不同的浮雕效果
- 快速处理，立即提供下载链接
- 简单的 REST API 接口

## 安装

### 前提条件

- Python 3.9+
- Docker（可选）

### 选项 1：本地安装

1. 克隆仓库：
```
git clone https://github.com/bigchx/mcp_3d_relief.git
cd mcp_3d_relief
```

2. 安装依赖：
```
pip install -r requirements.txt
```

3. 运行服务器：
```
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 选项 2：Docker

1. 构建 Docker 镜像：
```
docker build -t mcp_3d_relief .
```

2. 运行容器：
```
docker run -p 8000:8000 mcp_3d_relief
```

## 使用方法

### Web API

服务器运行后，可在 http://localhost:8000 访问 API。

#### 将图像转换为 STL

向 `/convert` 发送 POST 请求，包含以下表单数据：

- `file`：要转换的图像文件
- `model_width`：3D 模型的宽度（毫米，默认：50.0）
- `model_thickness`：3D 模型的最大厚度/高度（毫米，默认：5.0）
- `base_thickness`：底座厚度（毫米，默认：2.0）
- `skip_depth_conversion`：是否直接使用图像或生成深度图（默认：true）
- `invert_depth`：是否反转浮雕（明亮区域变低而不是高，默认：false）
- `detail_level`：控制处理图像的分辨率（默认：1.0）。当detail_level = 1.0时，图像以320px分辨率处理，生成的STL文件通常在100MB以内。较高的值可以提高细节质量，但会显著增加处理时间和STL文件大小。例如，将detail_level值加倍可能会使文件大小增加4倍或更多，请谨慎使用。

使用 curl 的示例：
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

### 响应

API 返回的 JSON 响应包含：

```json
{
  "status": "success",
  "depth_map_path": "output/yourimage_depth_map.png",
  "stl_path": "output/yourimage.stl",
  "depth_map_url": "/files/yourimage_depth_map.png",
  "stl_url": "/files/yourimage.stl"
}
```

您可以通过提供的 URL 直接访问生成的文件。

### 命令行

您也可以直接从命令行使用脚本：

```
python mcp_3d_relief.py '{"input_image": "example.jpg", "model_width": 50, "model_thickness": 5}'
```

### 外部深度图生成

为获得更高质量的深度图，您可以使用外部深度图生成服务，如 [Depth-Anything-V2](https://huggingface.co/spaces/depth-anything/Depth-Anything-V2)。该服务可以生成更准确的深度图，然后您可以将其用于本项目：

1. 访问 [https://huggingface.co/spaces/depth-anything/Depth-Anything-V2](https://huggingface.co/spaces/depth-anything/Depth-Anything-V2)
2. 上传您的图像以生成深度图
3. 下载生成的深度图
4. 将此深度图与我们的转换器一起使用，设置 `skip_depth_conversion=false`

这种方法可以提供更好的 3D 浮雕模型，特别是对于复杂图像。

## 工作原理

1. 处理图像创建深度图（较暗像素 = 较低，较亮像素 = 较高）
2. 将深度图转换为带有三角形面的 3D 网格
3. 在模型底部添加底座
4. 将模型保存为 STL 文件

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件 