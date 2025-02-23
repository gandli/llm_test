import os
import asyncio
import pyaudio
import wave
import pygame
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI
import edge_tts

# 从 .env 文件加载环境变量
load_dotenv()

# 初始化 Groq 
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 初始化 zhipu 
openai_client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
)

# 全局变量来保存对话历史
conversation_history = []

# 音频录制设置
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "test.wav"


# 录制音频函数
def record_audio():
    audio = pyaudio.PyAudio()

    # 开始录制
    stream = audio.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )
    print("录音开始...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束...")

    # 停止录制
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 保存录制的音频文件
    with wave.open(WAVE_OUTPUT_FILENAME, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))


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
    global conversation_history
    if not conversation_history:
        conversation_history.append({"role": "system", "content": "你是一个语音助手，请用简体中文回答问题。请确保回答简洁、自然，并且只使用纯文本，不使用任何格式化符号或Markdown语法。回答内容应适合合成语音。"})
    conversation_history.append({"role": "user", "content": prompt})

    completion_text = ""
    completion = openai_client.chat.completions.create(
        model="glm-4-flash",
        messages=conversation_history,
        top_p=0.7,
        temperature=0.9,
        stream=True,  # 启用流式输出
    )

    for chunk in completion:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
            completion_text += content

    conversation_history.append({"role": "assistant", "content": completion_text})

    return completion_text


# 使用 edge-tts 将文本转换为语音并保存为文件
async def text_to_speech(text, output_file):
    # 这里不再检查并删除文件，避免删除正在被使用的文件
    communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
    await communicate.save(output_file)


# 播放音频文件
def play_audio(file_path):
    pygame.mixer.init()  # 初始化pygame混音器
    pygame.mixer.music.load(file_path)  # 加载音频文件
    pygame.mixer.music.play()  # 播放音频文件

    # 等待音频播放结束
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()  # 确保文件被释放


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        while True:
            # 1. 录制音频
            record_audio()

            # 2. 转录音频文件
            print("正在转录音频...")
            transcribed_text = transcribe_audio(WAVE_OUTPUT_FILENAME)
            print(f"转录文本: {transcribed_text}\n")

            # 3. 基于转录文本生成对话
            print("生成对话内容...")
            completion_text = stream_chat_completion(transcribed_text)

            # 4. 使用 edge-tts 将对话内容转换为语音并保存
            output_audio_file = "output_audio.mp3"
            print("\n生成语音文件...")
            loop.run_until_complete(text_to_speech(completion_text, output_audio_file))

            # 5. 播放生成的语音
            print("\n播放生成的语音...")
            play_audio(output_audio_file)

            # 询问用户是否要继续对话
            cont = input("\n是否继续对话？(y/n): ")
            if cont.lower() != "y":
                break
    finally:
        loop.close()
        asyncio.set_event_loop(None)


if __name__ == "__main__":
    main()
