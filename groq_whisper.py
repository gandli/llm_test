import os
from dotenv import load_dotenv
from groq import Groq


def main():
    # 从 .env 文件加载环境变量
    load_dotenv()

    # 使用环境变量中的 API 密钥初始化 Groq 客户端
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # 定义音频文件路径
    filename = os.path.join(os.path.dirname(__file__), "test.m4a")

    # 处理音频文件并创建转录
    with open(filename, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=(filename, audio_file.read()),
            model="whisper-large-v3",
            language="zh",
            response_format="verbose_json",
        )

    # 输出转录文本
    print(transcription.text)


if __name__ == "__main__":
    main()
