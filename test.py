import discord
import asyncio
import require
from discord.ext import commands

# Create an instance of the bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
#  discord client

#  discord client
client = discord.Client(intents=discord.Intents.all())

# call when the bot is ready
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

# Command decorator to define a bot command
@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

# add note to the bot
@bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a+b)


# Run the bot using your bot token
bot.run(require.token)
