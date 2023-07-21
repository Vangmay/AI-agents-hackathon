import streamlit as st
from streamlit_chat import message
import openai
import cohere
from youtube_transcript_api import YouTubeTranscriptApi

data = ""

# Initialize the OpenAI and Cohere clients
# IF THIS WORKS THAN REMOVE LINE 13 and 14
openai.api_key = os.getenv["OPEN_AI_KEY"]
co = cohere.Client(os.getenv["COHERE_KEY"])
# openai.api_key = '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'
# co = cohere.Client('Ern5c8BvsiO8wrZguwKM5e2E3hJTITfDoGy6ktuv')

def audio_transcription(summary_info):
    if summary_info["input_type"] == "youtube":
         
        video_link = summary_info["link"]
        video_id = video_link.split("=")[-1]
        
        response = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([i["text"] for i in response])
        return text
    
    elif summary_info.get("input_type") == "local":
        file = summary_info.get("file")
        if not file:
           return "File is missing."

        try:
            
            # You may need to replace this line based on the specific speech-to-text service you're using
            transcript = openai.Audio.translate("whisper-1", file)
            return transcript["text"]
        except Exception as e:
           return str(e)

def summary(summary_info):

    
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

st.download_button(
    label="Download summary",
    data=data,
    file_name="summary.txt",
    mime="text/plain",
)
