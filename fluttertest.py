import flet as ft
from google.cloud import speech
import re
import sys
import pyperclip
from MicrophoneStream import MicrophoneStream
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import asyncio
from markdown import markdown
from prompt import prompt, classify_prompt
# Audio recording parameters
RATE = 16000
CHUNK = int(RATE * 5)  # 2000ms  # Flag to track recording status
Recording = False  # Initialize recording status
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code="en-US",
)
vertexai.init(project="devspeak-427714", location="us-central1")
model = GenerativeModel(
    "gemini-1.5-pro-001",
  )
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}
finals = ''
safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

def record_audio(e):
  global Recording
  if not Recording:
    # Start recording
    Recording = True
    e.control.text = "Recording..."
    e.control.update()


    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )
    import time
    ctime = time.time()
    client = speech.SpeechClient()
    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        responses = client.streaming_recognize(streaming_config, requests)
        # Now, put the transcription responses to use.
        listen_print_loop(responses, text_box)
        e.control.text = "Recording complete!"
        e.control.update()
        print("Done recording")
  else:
    # Stop recording
    Recording = False
    
    # Output the audio data (you can replace this with your desired output method)

def listen_print_loop(responses: object, text_box: ft.TextField) -> str:
    """
    """
    global Recording
    global finals
    finals = text_box.value
    print("Recording...")
    for response in responses:
        if not Recording:
            break
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue
        
        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript
        # Update the text box with the current transcripts
        if not result.is_final:
            text_box.value = finals + transcript
            print(transcript)
            text_box.update()
        else:
            finals += transcript
            # Update the text box with the current transcripts
            text_box.value = finals
            text_box.update()
            asyncio.run(generate_code(finals))
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b" , transcript, re.I) or not Recording :
                print("Exiting..")
                break
            if re.search(r"\b(reset|clear)\b", transcript, re.I):
                finals = ''
                print(finals)
                text_box.value = finals
                text_box.update()
                print("Cleared")
                continue
                

    return None
async def generate_code(transcript):
    global finals
    global gem_out
    print(transcript)
    cprompt = classify_prompt.format(Transcript = transcript)
    print("sending classifyt prompt")
    try:
      cout = model.generate_content([cprompt], generation_config=generation_config,)
    except:
      print("Failed to classify transcript")
      return
    if not re.search(r'\b(Finished and Code related)\b', cout.text, re.I):
       print("Code not generated", cout.text)
       return
    tpromt = prompt.format(Current=finals, Transcript=transcript)
    print("sending code prompt")
    try:
      out = model.generate_content([tpromt], generation_config=generation_config,)
    except:
      print("Failed to generate code")
      return
    print(out.text)
    gem_out.value = out.text
    finals = ''
    print(finals, "Generated")
    print(out.text, gem_out.value, "Updated")
    gem_out.update()
def main(page: ft.Page):
  global Recording
  def stop_recording(e):
    if Recording:
        Recording = False
        print("Recording stopped")

  global text_box
  page.title = "Audio Recorder"
  button = ft.ElevatedButton(
    text="Record Audio",
    on_click=record_audio
  )
  text_box = ft.TextField(
    multiline=True,
    expand=True,
  )
  global gem_out
  gem_out = ft.TextField(
    multiline=True,
    expand=True,
    read_only = True
  )
  def copy_text(e):
    pyperclip.copy(gem_out.value)  # Copy the text to the clipboard
    e.control.text = "Copied!"  # Update the button text
    e.control.update()
  copy_button = ft.ElevatedButton(
    text="Copy Text",
    on_click=copy_text
  )  
  page.on_window_close = lambda e: stop_recording(e)  # Handle window close
  page.add(button, text_box,gem_out, copy_button)

ft.app(target=main)
