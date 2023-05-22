#play the downloaded song on discord voice channel
import subprocess
import nest_asyncio
nest_asyncio.apply()
import os.path
import asyncio
import search_download
import discord
import require

# Discord authentication
client = discord.Client(intents=discord.Intents.all())
#call when the bos is ready
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

#call when a message is sent
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # check if the message is a play command
    if message.content.startswith('!play'):
        if not message.author.voice:
            await message.channel.send('You must be in a voice channel to use this command.')
            return
        channel = message.author.voice.channel
        #if the bot is not in the voice channel, connect to it
        if not message.guild.voice_client:
             await channel.connect()
        vc = message.guild.voice_client
    # search and download the song
        song_name = message.content[6:]
        search_download.check_song(song_name)
        while not os.path.exists(f"{search_download.song_search(song_name)[0]}.mp3"):
            await asyncio.sleep(1)
        loop.run_until_complete(search_download.check_song(song_name))

        #play the first song in the queue
        if len(search_download.song_search(song_name)) == 0:
            await message.channel.send('Song not found.')
            return
        await message.channel.send(f"Playing {search_download.song_search(song_name)[0]}")
        vc.play(discord.FFmpegPCMAudio(f"{search_download.play_list[0]}"))
    # check if the message is a queue command
    if message.content.startswith('!queue'):
        # check if the queue is empty
        if len(play_list) == 0:
            await message.channel.send('The queue is empty.')
            return
        # send the queue
        await message.channel.send('\n'.join(play_list))
    # skip current song and play the next song in the queue
    if message.content == '!skip':
        voice_client = message.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            await message.channel.send('Skipped.')
            await message.channel.send(f"Playing {play_list[0]}")
            voice_client = message.guild.voice_client
            voice_client.play(discord.FFmpegPCMAudio(f"{play_list[0]}.mp3"))
            while voice_client.is_playing():
                await asyncio.sleep(1)
            await voice_client.disconnect()
            play_list.pop(0)
    # pause the current song but not disconnect from the voice channel
    if message.content == '!pause':
        voice_client = message.guild.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            await message.channel.send('Paused.')
    # resume the current song
    if message.content == '!resume':
        voice_client = message.guild.voice_client
        if voice_client.is_paused():
            voice_client.resume()
            await message.channel.send('Resumed.')
    #clear the queue
    if message.content == '!clear':
        play_list.clear()
        await message.channel.send('The queue is cleared.')
    #leave the voice channel
    if message.content == '!leave':
        voice_client = message.guild.voice_client
        if voice_client.is_connected():
            await voice_client.disconnect()
            await message.channel.send('Disconnected.')

# run the bot
client.run(require.token)






