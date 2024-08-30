import os
from dotenv import load_dotenv
from openai import OpenAI

# 从 .env 文件加载环境变量
load_dotenv()

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)


# 从 API 流式获取聊天补全的函数
def stream_chat_completion():
    completion = client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是一个聪明且富有创造力的小说作家"},
            {
                "role": "user",
                "content": "请你作为童话故事大王，写一篇短篇童话故事，故事的主题是要永远保持一颗善良的心，要能够激发儿童的学习兴趣和想象力，同时也能够帮助儿童更好地理解和接受故事中所蕴含的道理和价值观。",
            },
        ],
        top_p=0.7,
        temperature=0.9,
        stream=True,  # 启用流式输出
    )

    # 遍历流式响应的每个数据块
    for chunk in completion:
        # 直接从 delta 对象访问 content 属性
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)


# 主入口
if __name__ == "__main__":
    stream_chat_completion()
