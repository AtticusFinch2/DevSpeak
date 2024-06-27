import flet as ft
import numpy as np
from google.cloud import speech
import re
import sys
import pyperclip
from MicrophoneStream import MicrophoneStream
# Audio recording parameters
RATE = 16000
CHUNK = int(RATE * 2)  # 2000ms  # Flag to track recording status
audio_data = np.array([])  # Initialize empty audio data arra
Recording = False  # Initialize recording status
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code="en-US",
)
def record_audio(e):
  global Recording
  if not Recording:
    # Start recording
    Recording = True
    e.control.text = "Recording..."
    e.control.update()
    print("Recording...")

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
        print("Done recording")
  else:
    # Stop recording
    Recording = False
    e.control.text = "Recording complete!"
    e.control.update()
    # Output the audio data (you can replace this with your desired output method)
def listen_print_loop(responses: object, text_box: ft.TextField) -> str:
    """Iterates through server responses and updates the text box.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    update the text box with the transcription for the top alternative of the
    top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, update the text box with the current transcript.
    For the final one, update the text box with the finalized transcription.

    Args:
        responses: List of server responses
        text_box: The Flutter text box to update.

    Returns:
        The transcribed text.
    """
    num_chars_printed = 0
    finals = ''
    global Recording
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
        #overwrite_chars = " " * (num_chars_printed - len(transcript))
        # Update the text box with the current transcripts
        if not result.is_final:
            text_box.value = finals + transcript
            print(text_box.value, num_chars_printed)
            text_box.update()
            #num_chars_printed = len(transcript)
        else:
            finals += transcript 
            text_box.value = finals
            text_box.update()
            #num_chars_printed = 0
            #print(Recording)
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b" , transcript, re.I) or not Recording :
                print("Exiting..")
                break

    return transcript

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
  def copy_text(e):
    pyperclip.copy(text_box.value)  # Copy the text to the clipboard
    e.control.text = "Copied!"  # Update the button text
    e.control.update()
  copy_button = ft.ElevatedButton(
    text="Copy Text",
    on_click=copy_text
  )  
  page.on_window_close = lambda e: stop_recording(e)  # Handle window close
  page.add(button, text_box, copy_button)

ft.app(target=main)
