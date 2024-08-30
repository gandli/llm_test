# Continuous Voice Chat

This project enables continuous voice-based conversation using a microphone for audio input and speakers for audio output. It transcribes audio, generates responses using a language model, and then synthesizes and plays the generated speech.

## Features

- **Real-time Transcription:** Converts spoken audio into text using Groq's Whisper model.
- **Language Model Interaction:** Generates intelligent responses using Zhipu AI's language model.
- **Text-to-Speech:** Converts the generated text into speech using edge-tts and plays it back.
- **Continuous Dialogue:** Supports ongoing conversation by listening, responding, and repeating.

## Prerequisites

- Python 3.7+
- A microphone for input and speakers for output
- A Groq API key (for transcription)
- A Zhipu AI API key (for language model responses)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/continuous_voice_chat.git
   cd continuous_voice_chat
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root directory and add your API keys:

   ```text
   GROQ_API_KEY=your_groq_api_key
   ZHIPU_API_KEY=your_zhipu_api_key
   ```

## Usage

1. Place your audio file in the project directory and name it `test.m4a`.
   
2. Run the script:

   ```bash
   python continuous_voice_chat.py
   ```

3. The script will:
   - Transcribe the audio file.
   - Generate a response based on the transcribed text.
   - Convert the response into speech and play it.

## Uninstall Zhipu AI SDK

If you need to uninstall the Zhipu AI SDK:

```bash
pip uninstall zhipuai
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to submit issues, fork the project, and send pull requests. Contributions are always welcome!
