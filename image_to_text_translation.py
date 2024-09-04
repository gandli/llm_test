import io
import os
import requests
from dotenv import load_dotenv
from PIL import Image, ImageOps

# 加载 .env 文件中的环境变量
load_dotenv()
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")

API_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/"
headers = {"Authorization": f"Bearer {API_TOKEN}"}


def run(model, input):
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response.json()


def image_to_int_array(image, format="PNG"):
    """Convert image to an array of unsigned 8-bit integers."""
    bytes_io = io.BytesIO()
    image.save(bytes_io, format=format)
    return list(bytes_io.getvalue())


def describe_and_translate_image(image_path):
    print(f"Processing: {image_path}")

    # 打开图片并调整大小
    img = Image.open(image_path)
    img = ImageOps.contain(img, (600, 600))

    # 调用 Cloudflare Workers AI 生成图像描述
    description_model = "@cf/unum/uform-gen2-qwen-500m"
    description_response = run(
        description_model,
        {
            "prompt": "Generate a caption for this image",
            "image": image_to_int_array(img),
        },
    )

    if (
        "result" in description_response
        and "description" in description_response["result"]
    ):
        description = description_response["result"]["description"]
        # print("描述:", description)

        # 使用 @cf/meta/m2m100-1.2b 模型翻译描述
        translation_model = "@cf/meta/m2m100-1.2b"
        translation_response = run(
            translation_model,
            {
                "text": description,
                "source_lang": "english",
                "target_lang": "chinese",
            },
        )

        if translation_response.get("result"):
            translated_description = translation_response["result"]["translated_text"]
            print("翻译后的描述:", translated_description)
        else:
            print("翻译失败:", translation_response)
    else:
        print("生成描述失败:", description_response)


def main():
    # 指定要遍历的目录
    images_dir = "images"

    # 遍历 images 目录下的所有 .jpg 和 .png 文件
    for file_name in os.listdir(images_dir):
        if file_name.lower().endswith(('.jpg', '.png')):
            # 获取完整的文件路径
            file_path = os.path.join(images_dir, file_name)
            describe_and_translate_image(file_path)


if __name__ == "__main__":
    main()