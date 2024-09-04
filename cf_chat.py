import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
AUTH_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")

prompt = "天空为什么是蓝色的？"
response = requests.post(
    f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/meta/llama-3.1-8b-instruct",
    headers={"Authorization": f"Bearer {AUTH_TOKEN}"},
    json={
        "stream": True,
        "messages": [
            {
                "role": "system",
                "content": "You are a friendly AI voice assistant. During phone conversations, your responses should be concise, to the point, and always in Simplified Chinese.",
            },
            {"role": "user", "content": prompt},
        ],
    },
    stream=True,
)

# 逐行读取响应数据
for line in response.iter_lines():
    if line:
        decoded_line = line.decode("utf-8")
        # print(decoded_line)
        if decoded_line.startswith("data:"):
            try:
                # 去掉 "data: " 前缀并解析为 JSON
                data = json.loads(decoded_line[6:])
                # 获取 response 字段的值
                response_content = data.get("response")
                if response_content:  # 只有在 response 不为空时才打印
                    print(response_content, end="")
            except json.JSONDecodeError:
                pass

response.close()
