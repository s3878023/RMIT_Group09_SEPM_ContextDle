import aiohttp
import argparse
import discord
import itertools
import json
import logging
import numpy as np
import random
import re
import shelve
import statistics
import responses

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameState:

  def __init__(self, word, result, story, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.word = word
    self.story = story
    self.guesses = {}
    self.result = result

  def migrate(self):
    if not hasattr(self, "result"):
      logging.info("migrate")
      self.result = self.guesses[self.word]

      def remove_vec(v):
        del v["vec"]
        return v

      self.guesses = dict([(k, remove_vec(v)) for k, v in self.guesses.items()
                           if "by" in v])
      return True
    else:
      return False

  def add_guess(self, guess, result):
    wa = self.result["vec"]
    ga = result["vec"]

    del result["vec"]
    result["similarity"] = np.dot(
      wa, ga) / (np.linalg.norm(wa) * np.linalg.norm(ga))

    self.guesses[guess] = result

  def maybe_add_author(self, guess, author):
    if not "by" in self.guesses[guess]:
      self.guesses[guess]["by"] = author

  def top(self):
    by_sim = [(v["similarity"], k) for (k, v) in self.guesses.items()]
    return [k for (_, k) in reversed(sorted(by_sim))]

  def hint(self):
    top = [self.guesses[guess] for guess in self.top()]

    if not top:
      return 1
    elif not "percentile" in top[0]:
      return 1
    elif 999 <= top[0]["percentile"]:
      n = top[0]["percentile"] - 1
      for g in top[1:]:
        if not "percentile" in g:
          break
        elif n > g["percentile"]:
          break
        else:
          n = g["percentile"] - 1
      return n
    else:
      return int((400 + top[0]["percentile"]) / 2)

  def is_guessed(self, guess):
    return guess in self.guesses

  def is_win(self, guess):
    return self.word == guess

  def scaled_similarity(self, similarity):
    s = similarity - self.story["rest"]
    s = s * 0.7 / (self.story["top"] - self.story["rest"])
    s = s + 0.2
    return 100 * s

  def format_win(self):
    g = self.guesses[self.word]
    return f'\N{confetti ball} {g["by"]} got the correct word `{self.word}`'

  def format_top(self, n):
    lines = [self.format_guess(guess) for guess in self.top()[:n]]
    text = "\n".join(lines)
    return f"```{text} ```"

  def format_stats(self):
    authors = {}
    hints = 0

    first = lambda t: t[0]
    by_author = sorted([(v["by"], v) for v in self.guesses.values()],
                       key=first)
    for author, guesses in itertools.groupby(by_author, key=first):
      if "hint" == author:
        hints = len([g for g in guesses])
      else:
        sims = [g[1]["similarity"] for g in guesses]
        oneks = [s for s in sims if s > self.story["rest"]]
        authors[author] = {
          "n": len(sims),
          "onek": len(oneks),
          "max": self.scaled_similarity(max(sims)),
          "median": self.scaled_similarity(statistics.median(sims)),
        }

    lines = [
      f"{len(self.guesses) - hints} guesses, {hints} hints", "",
      f'{"who":6} {"1k":>4} {"n":>4} {"max":>6}'
    ] + [
      f'{str(k)[:6]:6} {v["onek"]:4} {v["n"]:4} {round(v["max"], 2):6}'
      for k, v in sorted(authors.items(), key=lambda t: t[1]["max"])
    ]
    text = "\n".join(lines)
    return f"```{text}```"

  def format_guess(self, guess):

    def circle(percentile):
      s = self.scaled_similarity(g["similarity"])
      s = round(s, 2)
      percentile = s
      if percentile >= 90:
        return "FOUND !"
      elif percentile is not None:
        blocks = round(percentile / 10)
        return f"{'⭐' * blocks}{'⭑' * (9 - blocks)}"
      else:
        return "COLD"
      # if percentile >= 999:
      #   return "\N{confetti ball}"
      # elif percentile > 990:
      #   return "\N{large red circle}"
      # elif percentile > 900:
      #   return "\N{large orange circle}"
      # elif percentile > 750:
      #   return "\N{large yellow circle}"
      # elif percentile > 500:
      #   return "\N{large green circle}"
      # else:
      #   return "\N{large blue circle}"

    g = self.guesses[guess]

    if "percentile" in g:
      p = g["percentile"]
      percentile = f'{circle(int(p))}'
    elif g["similarity"] >= self.story["rest"]:
      percentile = "????\N{black question mark ornament}"
    else:
      percentile = "cold\N{snowman without snow}"

    s = self.scaled_similarity(g["similarity"])

    by = str(g["by"])[:6]

    return f"{guess:15} {round(s, 2):6} {percentile:>5}  {by:>6}"


class PlaySemantle(discord.Client):

  def __init__(self, channel, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.filter = re.compile("[^a-zA-Z]")

    with open("secretwords.json") as f:
      self.words = json.loads(f.read())

    self.games = shelve.open("play_semantle")

    for k in self.games.keys():
      g = self.games[k]
      if g.migrate():
        self.games[k] = g
    self.games.sync()

    self.channel = channel

  async def close(self):
    self.games.close()
    await super().close()

  async def on_ready(self):
    print(f'{client.user} is now running!!!')

  async def on_message(self, message):
    if message.author == self.user:
      return

    username = str(message.author)
    channel = str(message.channel)
    user_message = str(message.content)

    print(f'{username} said: "{user_message}" ({channel})')

    if message.author == self.user:
      pass

    elif not self.channel in message.channel.name:
      pass

    else:
      if not str(message.channel.id) in self.games:
        word = random.choice(self.words)

        result = await self.result(word, word)
        story = await self.story(word)

        self.games[str(message.channel.id)] = GameState(word, result, story)
        self.games.sync()

        logger.debug(
          f"{message.channel}({str(message.channel.id)})'s' word is {word}")

      elif message.content.startswith("!new"):
        await self.process_new(message)
        await message.channel.send('new')

      elif message.content.startswith("!hint"):
        await self.process_hint(message)

      elif message.content.startswith("!guess"):
        guess = self.filter.sub("", message.content[7:])
        await self.process_guess(message, str(message.author), guess)

      elif message.content.startswith("$"):
        guess = self.filter.sub("", message.content[1:])
        await self.process_guess(message, str(message.author), guess)

      elif message.content.startswith("!top"):
        try:
          n = int(message.content.split(" ")[1])
        except:
          n = 10

        await self.process_top(message, n)

      elif message.content.startswith("!stats"):
        await self.process_stats(message)

      elif user_message[0] == '?':
        user_message = user_message[1:]
        await self.send_message(message, user_message, is_private=True)
      else:
        await self.send_message(message, user_message, is_private=False)

  async def process_stats(self, message):
    game = self.games[str(message.channel.id)]
    await message.channel.send(game.format_stats())

  async def process_new(self, message):
    game = self.games[str(message.channel.id)]

    await message.channel.send(game.format_top(20))
    await message.channel.send(game.format_stats())
    await message.channel.send(
      f'Old word was  *{game.word}*. Choosing a new word')

    del self.games[str(message.channel.id)]
    self.games.sync()

  async def process_hint(self, message):
    game = self.games[str(message.channel.id)]

    n = game.hint()
    hint = await self.nth_nearby(game.word, n)

    await self.process_guess(message, "hint", hint)

  async def process_top(self, message, n):
    game = self.games[str(message.channel.id)]
    await message.channel.send(game.format_top(n))

  async def process_guess(self, message, author, guess):
    game = self.games[str(message.channel.id)]
    try:
      if not game.is_guessed(guess):
        result = await self.result(game.word, guess)

      game = self.games[str(message.channel.id)]

      if not game.is_guessed(guess):
        game.add_guess(guess, result)

      game.maybe_add_author(guess, author)

      self.games[str(message.channel.id)] = game
      self.games.sync()

      if game.is_win(guess):
        await message.channel.send(game.format_win())
        await message.channel.send(game.format_top(20))
        await message.channel.send(game.format_stats())
      else:
        await message.channel.send(f"```{game.format_guess(guess)} ```")

    except json.decoder.JSONDecodeError:
      await message.channel.send(f"{guess} is invalid")

  async def story(self, word):
    async with aiohttp.ClientSession() as session:
      async with session.get(
          f"http://semantle.com/similarity/{word}") as response:
        text = await response.text()
        result = json.loads(text)
        return result

  async def result(self, word, guess):
    async with aiohttp.ClientSession() as session:
      async with session.get(
          f"http://semantle.com/model2/{word}/{guess}") as response:
        text = await response.text()
        result = json.loads(text)
        result["vec"] = np.array(result["vec"])
        return result

  async def nth_nearby(self, word, n):
    async with aiohttp.ClientSession() as session:
      async with session.get(
          f"http://semantle.com/nth_nearby/{word}/{n}") as response:
        text = await response.text()
        result = json.loads(text)
        return result

  async def send_message(self, message, user_message, is_private):
    try:
      response = responses.get_response(user_message)
      await message.author.send(
        response) if is_private else await message.channel.send(response)

    except Exception as e:
      print(e)


parser = argparse.ArgumentParser(description="Semantle bot")
parser.add_argument("-d", "--debug", action="store_true")
parser.add_argument(
  "-t",
  "--token",
  default=
  "MTA5MjMwODkyODcyNzEwMTUwMA.GDWRjl.fGctuNZxpDzBntxDMIartq2iJFW__Ao42Cbjng")
parser.add_argument("-c", "--channel", default="semantle")

args = parser.parse_args()

if args.debug:
  logger.setLevel(logging.DEBUG)

client = PlaySemantle(args.channel,
                      command_prefix='!',
                      intents=discord.Intents.all())

client.run(args.token)
