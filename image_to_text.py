import io
import os
import requests
from dotenv import load_dotenv
from PIL import Image, ImageOps

# 加载 .env 文件中的环境变量
load_dotenv()
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")


def image_to_int_array(image, format="PNG"):
    """Convert image to an array of unsigned 8-bit integers."""
    bytes_io = io.BytesIO()
    image.save(bytes_io, format=format)
    return list(bytes_io.getvalue())


def main():
    # 设置 prompt 和 image_path
    prompt = "Generate a caption for this image"
    image_path = "cat (1).jpg"

    # 打开图片并调整大小
    img = Image.open(image_path)
    img = ImageOps.contain(img, (600, 600))

    # 调用 Cloudflare Workers AI API
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
    }

    model = "@cf/unum/uform-gen2-qwen-500m"
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{model}"

    response = requests.post(
        url,
        headers=headers,
        json={
            "prompt": prompt,
            "image": image_to_int_array(img),
        },
    )

    # 处理并显示响应
    if response.ok:
        json_response = response.json()
        print("描述:", json_response["result"]["description"])
    else:
        print("Error:", response.status_code)
        print(response.reason)
        print(response.content)


if __name__ == "__main__":
    main()
