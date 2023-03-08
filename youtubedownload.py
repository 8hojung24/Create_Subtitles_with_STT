from pytube import YouTube
import ffmpeg
from google.cloud import storage
from google.oauth2 import service_account
from google.cloud import speech
import srt
import os


url = "https://www.youtube.com/watch?v=oYnfsg-l0KM"
yt = YouTube(url)

""""""""" Youtube 영상 다운 """""""""
DOWNLOAD_FOLDER = "C:\\Users\\8hoju\\OneDrive\\바탕 화면\\College\\인터루드\\23.01 영상자막\\영상example"
stream = yt.streams.get_highest_resolution()
stream.download(DOWNLOAD_FOLDER)
print(yt.title)