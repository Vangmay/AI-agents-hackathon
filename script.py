import streamlit as st
from streamlit_chat import message
import openai
import cohere
from pydub import AudioSegment
import os
from pytube import YouTube

data = ""
# Initialize the OpenAI and Cohere clients
openai.api_key = os.getenv["OPEN_AI_KEY"]
co = cohere.Client(os.getenv["COHERE_KEY"])

# openai.api_key = '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'
# co = cohere.Client('Ern5c8BvsiO8wrZguwKM5e2E3hJTITfDoGy6ktuv')

def download(URL):
    # This function downloads the URL using Pytube and returns the path of the audio file
    AUDIO_SAVE = "./audio"
    audio = YouTube(URL).streams.filter(only_audio=True).first()
    try:
        audio.download(AUDIO_SAVE)
    except:
        print("FAILED TO GET VIDEO, PLEASE CHECK YOUR URL AND ENSURE VIDEO IS NOT PRIVATE")

    audio_path = os.path.join(AUDIO_SAVE, os.listdir(AUDIO_SAVE)[0])
    print("AUDIO DOWNLOADED SUCCESSFULLY")
    return audio_path

#Get the transcription
def audio_transcription(summary_info):
    if summary_info["input_type"] == "youtube":
        URL = summary_info["link"]
        path = download(URL)
        # Implement the transcription using OpenAI's Whisper ASR API
        
    
        # Open the file in binary mode and then pass it to the OpenAI API
        with open(path, "rb") as file:
           transcript = openai.Audio.translate("whisper-1", file)

        # Remove the audio file after transcription
        os.remove(path)
        return transcript["text"]
    
 
    
    elif summary_info.get("input_type") == "local":
        file = summary_info.get("file")
        if not file:
           return "File is missing."

        try:
            # Check the size of the file
            file_size = file.size / (1024 * 1024)  # Changed this line
            if file_size > 25:
                # Split audio file into 10 minute segments if file size is larger than 25 MB
                song = AudioSegment.from_mp3(file)
                ten_minutes = 10 * 60 * 1000

                parts = len(song) // ten_minutes
                transcripts = []

                for i in range(parts + 1):
                    # export each part and get the transcript
                    part = song[i*ten_minutes:(i+1)*ten_minutes]
                    part.export("temp.mp3", format="mp3")
                    
                    # replace this line based on the specific speech-to-text service you're using
                    transcript = openai.Audio.translate("whisper-1", "temp.mp3")
                    transcripts.append(transcript["text"])
                
                return " ".join(transcripts)

            else:
                # You may need to replace this line based on the specific speech-to-text service you're using
                transcript = openai.Audio.translate("whisper-1", file)
                return transcript["text"]
            
        except Exception as e:
           return str(e)

def summary(summary_info):
    try:
        text_to_summarize = audio_transcription(summary_info)

        response = co.summarize(
            model=summary_info['model'],
            text=text_to_summarize,
            length=summary_info['length'],
            format=summary_info['format'],
            extractiveness='medium'
        )
        summary = response.summary

        return summary
    except cohere.CohereAPIError as e:
        print(f"Could not generate summary due to the following error: {e}")
        return None

def write_to_file(filename, data):
    with open(filename, 'w') as file:
        file.write(data)
    return data

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
    model = st.radio(
        "Select a summarizing model:",
        ("summarize-xlarge", "summarize-medium")
    )
    length = st.radio(
        "Select desired length of summary:",
        ("short", "medium", "long")
    )
    format = st.radio(
        "Select summarize text format:",
        ("bullets", "paragraph")
    )
    
    if st.form_submit_button("Generate Summary"):
        # Correctly populate the summary_info dictionary with user inputs
        
        summary_info = {
            "input_type": input_type,
            "link": link,
            "file": file,
            "model": model,
            "length": length,
            "format": format
        }

        
        data = write_to_file('summary.txt', summary(summary_info))
        tts = gTTS(data, lang='en')
        tts.save('summary.mp3')

if data:
    st.download_button(
        label="Download summary text",
        data=data,
        file_name="summary.txt",
        mime="text/plain",
    )

    # Button to download the audio summary
    st.download_button(
        label="Download audio summary",
        data=open('summary.mp3', 'rb'),
        file_name="summary.mp3",
        mime="audio/mpeg",
    )






