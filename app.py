import streamlit as st
import smtplib
import pytube
import os
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pytube import YouTube
from youtube_search import YoutubeSearch
import pydub
from pydub import AudioSegment
import time
import requests

st.set_page_config("Mashup🥁")
st.title("Mashup 🥁")

def download_audio_from_search(singer, n, m):
    results = YoutubeSearch(singer, max_results=m).to_dict()
    for i, result in enumerate(results):
        video_url = "https://www.youtube.com/watch?v=" + result["id"]
        try:
            yt = YouTube(video_url)
            stream = yt.streams.filter(only_audio=True).first()
            stream.download(filename=f"{singer}_{i}.mp4")
            audio = pydub.AudioSegment.from_file(f"{singer}_{i}.mp4")
            audio = audio[:n * 1000]
            audio.export(f"{singer}_{i}.mp3", format="mp3")
            st.write(f"Audio of {n} seconds from {yt.title} downloaded and converted to MP3 successfully")
        except pytube.exceptions.RegexMatchError as e:
            st.error(f"Error downloading video: {e}")
            st.error("It seems like YouTube has updated its site. Please update PyTube or try again later.")
            return False
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            return False
    return True

def combine_audio_files(singer, n, m):
    combined = AudioSegment.empty()
    for i in range(m):
        audio = AudioSegment.from_file(f"{singer}_{i}.mp3")
        combined += audio
    combined.export(f"{singer}_combined.mp3", format="mp3")
    st.write(f"All audio files combined into a single file: {singer}_combined.mp3")

def sendMail(recp):
    sender = st.secrets["SMTP_MAIL"]
    recipient = recp
    password = st.secrets["SMTP_PASS"]
    subject = 'Combined Audio File'
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    text = MIMEText(f'Please find the attached the combined audio file of {singer}')
    msg.attach(text)
    audi = MIMEAudio(open(f'{singer}_combined.mp3', 'rb').read(), 'mp3')
    msg.attach(audi)
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(sender, password)
    smtp.sendmail(sender, recipient, msg.as_string())
    smtp.quit()

singer = st.text_input("Singer Name:")
m = st.number_input("Number of Videos:", min_value=10, max_value=50)
n = st.number_input("Duration of each Audio Clip (in seconds):", min_value=20, max_value=90)
recp = st.text_input("Email To:")
bt1 = st.button("Combine and Send Mail")

if bt1:
    with st.spinner('Preparing Audio... (this may take up to a few minutes)'):
        if download_audio_from_search(singer, n, m):
            combine_audio_files(singer, n, m)
            sendMail(recp)
            st.success('Your file was mailed successfully!')
        else:
            st.error("Failed to download audio files. Please try again later.")
