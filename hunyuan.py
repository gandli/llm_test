import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

agent_id = os.getenv("YUANQI_AGENT_ID")
token = os.getenv("YUANQI_AGENT_TOKEN")

# 定义 API 的 URL
url = 'https://open.hunyuan.tencent.com/openapi/v1/agent/chat/completions'

# 定义请求头
headers = {
    'X-Source': 'openapi',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}'
}

# 定义请求体
data = {
    "assistant_id": agent_id,
    "user_id": "username",
    "stream": True,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "六个严禁是指什么？"
                }
            ]
        }
    ]
}

# 将请求体转换为 JSON 格式的字符串
json_data = json.dumps(data)

# 发送 POST 请求
response = requests.post(url, headers=headers, json=data)  

# 检查请求是否成功
# if response.status_code == 200:
#     # 解析 JSON 响应
#     response_data = response.json()
#     # 提取 content 字段
#     content = response_data['choices'][0]['message']['content']
#     # 打印 content
#     print(content)
# else:
#     print(f"请求失败，状态码: {response.status_code}")
#     print(response.text)
if response.status_code == 200:
    # 逐行读取流式返回的数据
    for line in response.iter_lines():
        if line:  # 检查行是否为空
            decoded_line = line.decode('utf-8').strip()  # 解码并移除首尾空白字符
            # print(decoded_line)
            if decoded_line.startswith("data:"):  # 检查是否包含数据
                decoded_line = decoded_line[5:].strip()  # 移除前缀 "data: "
                try:
                    json_data = json.loads(decoded_line)
                    # 仅提取 role 为 assistant 的 content
                    delta = json_data['choices'][0]['delta']
                    if delta.get('role') == 'assistant':
                        content = delta.get('content')
                        if content:  # 如果 content 存在，则打印
                            print(content,end='')
                except json.JSONDecodeError:
                    pass  
else:
    print(f"请求失败，状态码: {response.status_code}")
    print(response.text)