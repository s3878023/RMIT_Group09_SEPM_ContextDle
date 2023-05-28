# ContextDle
A multipurpose bot affering Semantle game and music feature.

## how to set up

### invite link
https://discord.com/api/oauth2/authorize?client_id=1092308928727101500&permissions=8&scope=bot

### channel setup
- The bot will only respond to messages in channels that include `contextdle` in their name, like `#contextdle` or `#play-contextdle`

- Each channel has a separate game state

## differences from http://semantle.com
- Guess similarity is scaled s.t. the 1000th closest word has similarity 20.0 and the closest word has similarity 90.0

## commands

### `!guess <WORD>`
Make a guess in the game; the bot will respond with the score for the word or phrase

### `$<WORD>`
Shorthand for `!guess`

### `!top <N>`
She bot will respond with a list of the top N guesses and their scores; defaults to `10` if no argument is specified

### `!hint`
The bot will respond with a hint

### `!new`
The bot will report the top guesses and answer for the previous game, then select a new word
