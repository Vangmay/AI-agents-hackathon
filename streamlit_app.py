import streamlit as st
from streamlit_chat import message
import openai
import os 
import torch
import whisper
import numpy as np
from pytube import YouTube
import argparse
# import cohere
# from youtube_transcript_api import YouTubeTranscriptApi

# Initialize the OpenAI and Cohere clients
openai.api_key = 'Your Api Key'
# co = cohere.Client('Ern5c8BvsiO8wrZguwKM5e2E3hJTITfDoGy6ktuv')


def download(URL):
  """
  This function downloads the URL using some libraries and then
  it will return the path of this audio
  """
  AUDIO_SAVE = "./audio"
  audio = YouTube(URL).streams.filter(only_audio = True).first() 
  try:
      audio.download(AUDIO_SAVE)
  except:
      print("FAILED TO GET VIDEO, PLEASE CHECK YOUR URL AND ENSURE VIDEO IS NOT PRIVATE")

  audio_path = os.path.join(AUDIO_SAVE, os.listdir(AUDIO_SAVE)[0])
  print("AUDIO DOWNLOADED SUCCESSFULLY")
  return audio_path

def audio_transcription(summary_info):
    if summary_info["input_type"] == "youtube":
        URL = summary_info["link"]
        path = download(URL)
        audio = whisper.load_audio(path)
        audio = whisper.pad_or_trim(audio)
        processed_audio = whisper.log_mel_spectrogram(audio).to(model.device)

        torch.cuda.is_available()
        DEVICE = "cuda" if torch.cuda.is_available() else "cpy"

        model = whisper.load_model("base", device = DEVICE)

        ## CHECKING LANGUAGE OF LECTURE
        _, probs = model.detect_language(processed_audio)
        language = max(probs, key=probs.get)


        result = model.transcribe(path)
        os.remove(path)
        return result["text"]

        # video_link = summary_info["link"]
        # video_id = video_link.split("=")[-1]
        
        # response = YouTubeTranscriptApi.get_transcript(video_id)
        # text = " ".join([i["text"] for i in response])
        # return text
    
    if summary_info.get("input_type") == "local":
        file = summary_info.get("file")
        if not file:
           return "File is missing."

        try:
            # Read file data directly if file is an UploadedFile object
            audio_data = file.read()
        
            # You may need to replace this line based on the specific speech-to-text service you're using
            transcript = openai.Audio.translate("whisper-1", audio_data)
            return transcript["text"]
        except Exception as e:
           return str(e)


# Initialize session state

st.header("Summary Information")

input_type = st.radio(
        "Select the input type:",
        ("youtube", "local")
    )
if input_type == "youtube":
            link = st.text_input("Input YouTube link:")
            file = None
elif input_type == "local":
            file = st.file_uploader("Upload local audio or video file:", type=["mp3", "wav", "mp4"])
            link = None
  
with st.form("summary_info"):   
    
    if st.form_submit_button("Generate Summary"):
        # Correctly populate the summary_info dictionary with user inputs
        
        summary_info = {
            "input_type": input_type,
            "link": link,
            "file": file,
            
        }

        final_summary = audio_transcription(summary_info)
        st.text(final_summary)
