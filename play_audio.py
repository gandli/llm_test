import pygame


def play_audio(file_path):
    # 初始化pygame混音器
    pygame.mixer.init()

    # 加载音频文件
    pygame.mixer.music.load(file_path)

    # 播放音频文件
    pygame.mixer.music.play()

    # 等待音频播放结束
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


if __name__ == "__main__":
    audio_file = "output_audio.mp3"
    play_audio(audio_file)
