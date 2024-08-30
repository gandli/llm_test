import os
import asyncio
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
import edge_tts
import subprocess

# 从 .env 文件加载环境变量
load_dotenv()

# 初始化 Groq 客户端
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 初始化 OpenAI 客户端
openai_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)


# 音频转录函数
def transcribe_audio(filename):
    with open(filename, "rb") as audio_file:
        transcription = groq_client.audio.transcriptions.create(
            file=(filename, audio_file.read()),
            model="whisper-large-v3",
            language="zh",
            response_format="verbose_json",
        )
    return transcription.text


# 从 API 流式获取聊天补全的函数，并将其返回
def stream_chat_completion(prompt):
    completion_text = ""
    completion = openai_client.chat.completions.create(
        model="glm-4-flash",
        messages=[
            {"role": "system", "content": "你是一个人工智能语音助手。你的回答应该始终贴近口语，纯文本不要使用markdown语法，以方便合成为语音。"},
            {"role": "user", "content": prompt},
        ],
        top_p=0.7,
        temperature=0.9,
        stream=True,  # 启用流式输出
    )

    # 遍历流式响应的每个数据块
    for chunk in completion:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
            completion_text += content

    return completion_text


# 使用 edge-tts 将文本转换为语音并保存为文件
async def text_to_speech(text, output_file):
    communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
    await communicate.save(output_file)


# 播放音频文件
def play_audio(file_path):
    if os.name == "nt":  # Windows
        os.startfile(file_path)
    elif os.name == "posix":  # macOS or Linux
        subprocess.call(["open", file_path])


def main():
    # 定义音频文件路径
    audio_filename = os.path.join(os.path.dirname(__file__), "test.m4a")

    # 1. 转录音频文件
    print("正在转录音频...")
    transcribed_text = transcribe_audio(audio_filename)
    print(f"转录文本: {transcribed_text}\n")

    # 2. 基于转录文本生成对话
    print("生成对话内容...")
    completion_text = stream_chat_completion(transcribed_text)

    # 3. 使用 edge-tts 将对话内容转换为语音并保存
    output_audio_file = "output_audio.mp3"
    print("\n生成语音文件...")
    asyncio.run(text_to_speech(completion_text, output_audio_file))

    # 4. 播放生成的语音
    print("\n播放生成的语音...")
    play_audio(output_audio_file)


if __name__ == "__main__":
    main()
