# search using spotipy and download using spotdl
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotdl import Spotdl
import require
import os
import nest_asyncio
nest_asyncio.apply()


# search for song using spotipy
#create play list
play_list = []
def song_search(query):
    sp = spotipy.Spotify(
        client_credentials_manager=SpotifyClientCredentials(client_id=require.clientID, client_secret=require.secretID))
    results = sp.search(q=query, type='track', limit=1)
    song_name = results['tracks']['items'][0]['name']
    artist = results['tracks']['items'][0]['artists'][0]['name']
    URL = results['tracks']['items'][0]['external_urls']['spotify']
    track = f"{artist} - {song_name}"
    return track, URL

# download song using spotdl
async def download_song(url):
    spotdl = Spotdl(client_id=require.clientID, client_secret=require.secretID)
    song = spotdl.search([url])
    await spotdl.download_songs(song)



# check if song is already downloaded
async def check_song(search):
    song_path = f"{song_search(search)[0]}.mp3"
    if os.path.isfile(song_path):
        play_list.append(song_path)
        print("song already downloaded")
    else:
        print("downloading song")
        await download_song(song_search(search)[1])
        play_list.append(song_path)
        print("download complete")
    return song_path


