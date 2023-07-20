import streamlit as st
from streamlit_chat import message
import openai
# import cohere
# from youtube_transcript_api import YouTubeTranscriptApi

# Initialize the OpenAI and Cohere clients
openai.api_key = 'Your Api Key'
# co = cohere.Client('Ern5c8BvsiO8wrZguwKM5e2E3hJTITfDoGy6ktuv')

def audio_transcription(summary_info):
    # if summary_info["input_type"] == "youtube":
    #     video_link = summary_info["link"]
    #     video_id = video_link.split("=")[-1]
        
    #     response = YouTubeTranscriptApi.get_transcript(video_id)
    #     text = " ".join([i["text"] for i in response])
    #     return text
    
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
