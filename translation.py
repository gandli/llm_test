import requests
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()
ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")

API_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/"
headers = {"Authorization": f"Bearer {API_TOKEN}"}


def run(model, input):
    response = requests.post(f"{API_BASE_URL}{model}", headers=headers, json=input)
    return response.json()


output = run(
    "@cf/meta/m2m100-1.2b",
    {
        "text": "I'll have an order of the moule frites",
        "source_lang": "english",
        "target_lang": "chinese",
    },
)

print(output)
