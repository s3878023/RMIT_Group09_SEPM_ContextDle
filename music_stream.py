import spotipy
import discord
import search_download
import require
import asyncio

#  discord client
client = discord.Client(intents=discord.Intents.all())

# list of songs in the queue
play_list = []

# call when the bot is ready
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

# call when a message is sent
@client.event
async def on_message(message):
    # check if the message is sent by the bot
    if message.author == client.user:
        return
    # check if the message is a play command
    if message.content.startswith('!play'):
        # check if the user is in a voice channel
        if not message.author.voice:
            await message.channel.send('You must be in a voice channel to use this command.')
            return
        channel = message.author.voice.channel
        # if the bot is not in the voice channel, connect to it
        if not message.guild.voice_client:
            await channel.connect()
        vc = message.guild.voice_client

        # search for the song on spotify
        song_name = message.content[6:]
        track = search_download.song_search(song_name)

        # add the song to the queue
        play_list.append(f"{track[0]}")
        # check if the song is already downloaded
        search_download.check_song(track[0])
        # play the all the song in the play list, remove the song from the queue when it is done playing
        if vc.is_playing():
            await message.channel.send(f"Added {track[0]} to the queue.")
        else:
            await message.channel.send(f"Playing {track[0]}")
            vc.play(discord.FFmpegPCMAudio(f"{track[0]}.mp3"))
            while vc.is_playing():
                await asyncio.sleep(1)
            play_list.pop(0)
    # display song name and order in the queue
    if message.content.startswith('!queue'):
        # check if the queue is empty
        if len(play_list) == 0:
            await message.channel.send('The queue is empty.')
            return
        # send the queue
        for i in range(len(play_list)):
            await message.channel.send(f"{i+1}. {play_list[i]}")
    # skip current song and play the next song in the queue
    if message.content == '!skip':
        voice_client = message.guild.voice_client
        voice_client.stop()
        await asyncio.sleep(1)
        if len(play_list) == 0:
            await message.channel.send('The queue is empty.')
            return
        await message.channel.send(f"Playing {play_list[0]}")
        voice_client.play(discord.FFmpegPCMAudio(f"{play_list[0]}.mp3"))
        while voice_client.is_playing():
            await asyncio.sleep(1)
        play_list.pop(0)
    # pause the current song
    if message.content == '!pause':
        voice_client = message.guild.voice_client
        voice_client.pause()
    # resume the current song
    if message.content == '!resume':
        voice_client = message.guild.voice_client
        voice_client.resume()
    # stop the music, clear the queue, and disconnect from the voice channel
    if message.content == '!stop':
        voice_client = message.guild.voice_client
        voice_client.stop()
        play_list.clear()
        await voice_client.disconnect()
# run the bot
client.run(require.token)