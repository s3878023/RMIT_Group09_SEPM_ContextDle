# search using spotipy and download using spotdl
import spotipy as spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotdl import Spotdl
import require
import os
import asyncio


# search for song using spotipy

def song_search(query):
    sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id=require.clientID, client_secret=require.secretID))
    results = sp.search(q=query, type='track', limit=1)
    song_name = results['tracks']['items'][0]['name']
    artist = results['tracks']['items'][0]['artists'][0]['name']
    URL = results['tracks']['items'][0]['external_urls']['spotify']
    track = f"{artist} - {song_name}"
    return track, URL


# download song using spotdl and save in folder music
def download_song(url):
    spotdl = Spotdl(client_id=require.clientID, client_secret=require.secretID)
    song = spotdl.search([url])
    spotdl.download_songs(song)


# check if song is already downloaded
def check_song(search):
    song_path = f"{song_search(search)[0]}.mp3"
    if os.path.isfile(song_path):
        print("song already downloaded")
    else:
        print("downloading song")
        download_song(song_search(search)[1])
        print("download complete")


# # test
# query = input("Enter a Spotify URL (or 'q' to quit): ")
#
# check_song(query)
