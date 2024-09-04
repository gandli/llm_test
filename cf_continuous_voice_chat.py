import os
import asyncio
import pyaudio
import wave
import pygame
from dotenv import load_dotenv
import requests
import json
import edge_tts

# 从 .env 文件加载环境变量
load_dotenv()

# Cloudflare API 设置
cloudflare_account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID")
cloudflare_api_token = os.getenv("CLOUDFLARE_API_TOKEN")

# 全局变量来保存对话历史
conversation_history = []

# 音频录制设置
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10
WAVE_OUTPUT_FILENAME = "test.wav"


# 录制音频函数
def record_audio():
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )
    print("录音开始...")

    frames = []
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束...")
    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))


# 音频转录函数
def transcribe_audio(filename):
    with open(filename, "rb") as audio_file:
        url = f"https://api.cloudflare.com/client/v4/accounts/{cloudflare_account_id}/ai/run/@cf/openai/whisper"
        headers = {
            "Authorization": f"Bearer {cloudflare_api_token}",
        }
        response = requests.post(url, headers=headers, data=audio_file)
        response_data = response.json()
        return response_data.get("result", {}).get("text", "")


# 从 API 流式获取聊天补全的函数，并将其返回
def stream_chat_completion(prompt):
    global conversation_history
    if not conversation_history:
        conversation_history.append(
            {
                "role": "system",
                "content": "You are a friendly AI voice assistant. During phone conversations, your responses should be concise, to the point, and always in Simplified Chinese. Ensure your answers are natural and fluent, using plain text only, avoiding any formatting symbols or Markdown syntax, and the content should be suitable for speech synthesis.",
            }
        )
    conversation_history.append({"role": "user", "content": prompt})

    completion_text = ""
    url = f"https://api.cloudflare.com/client/v4/accounts/{cloudflare_account_id}/ai/run/@cf/qwen/qwen1.5-14b-chat-awq"
    headers = {"Authorization": f"Bearer {cloudflare_api_token}"}
    response = requests.post(
        url,
        headers=headers,
        json={
            "stream": True,
            "messages": conversation_history,
        },
        stream=True,
    )

    for line in response.iter_lines():
        if line:
            decoded_line = line.decode("utf-8")
            if decoded_line.startswith("data:"):
                try:
                    data = json.loads(decoded_line[6:])
                    response_content = data.get("response")
                    if response_content:
                        print(response_content, end="", flush=True)
                        completion_text += response_content
                except json.JSONDecodeError:
                    pass

    conversation_history.append({"role": "assistant", "content": completion_text})
    return completion_text


# 使用 edge-tts 将文本转换为语音并保存为文件
async def text_to_speech(text, output_file):
    communicate = edge_tts.Communicate(text, voice="zh-CN-XiaoxiaoNeural")
    await communicate.save(output_file)


# 播放音频文件
def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.unload()


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        while True:
            record_audio()
            print("正在转录音频...")
            transcribed_text = transcribe_audio(WAVE_OUTPUT_FILENAME)
            print(f"转录文本: {transcribed_text}\n")

            print("生成对话内容...")
            completion_text = stream_chat_completion(transcribed_text)

            output_audio_file = "output_audio.mp3"
            print("\n生成语音文件...")
            loop.run_until_complete(text_to_speech(completion_text, output_audio_file))

            print("\n播放生成的语音...")
            play_audio(output_audio_file)

            # 继续对话，无需用户输入，只在用户按下 Ctrl+C 时退出
    except KeyboardInterrupt:
        print("\n对话已终止。")
    finally:
        loop.close()
        asyncio.set_event_loop(None)


if __name__ == "__main__":
    main()
