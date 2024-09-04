import os
from dotenv import load_dotenv
import requests

load_dotenv()
# 替换为你的 Cloudflare 账户 ID 和 API Token
ACCOUNT_ID=os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN=os.environ.get("CLOUDFLARE_API_TOKEN")

# 设置请求 URL
url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/openai/whisper"

# 设置请求头
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
}

# 读取文件内容
file_path = "output_audio.mp3"
with open(file_path, "rb") as file:
    file_data = file.read()

# 发送 POST 请求
response = requests.post(url, headers=headers, data=file_data)

# 打印响应
# print(response.status_code)
# print(response.json())
print(response.json()["result"]["text"])