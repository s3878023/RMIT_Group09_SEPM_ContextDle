import discord
import os
import asyncio
import youtube_dl

#waiting for the token needed#
token = "waiting for token"

client = discord.Client()

#use this to content the block word for cursing#
block_words = ["peepee", "poopoo"]


#create the event for bot to interact and behave#
@client.event
async def on_ready(): 
    print(f"Bot has joined the chat as {client.user}")

@client.event
async def on_message(msg):
    if msg.author != client.user: 
        if msg.content.lower().startswith("/hi"): 
            await msg.channel.send(f"Hi, {msg.author.display_name}")
        for text in block_words:
            if "Moderator" not in str(msg.author.roles) and text in str(msg.content.lower()):
                await msg.delete()
                return
        
client.run(token)