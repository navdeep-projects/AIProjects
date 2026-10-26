"""Read text and speak in female voice"""
from pathlib import Path
from openai import OpenAI
from IPython.display import Audio, display

class femalevoice:
    """Class to generate female voice from text"""
    
    @staticmethod
    def generate_voice( message: str, output_file: str):
        client = OpenAI()
        output_path = Path(output_file)
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="coral",
            input=message,
            instructions="Speak warmly and clearly, like a friendly female assistant.",
        ) as response:
            response.stream_to_file(output_path)
        display(Audio(filename=str(output_path)))
        print(f"Voice note saved: {output_path}")


