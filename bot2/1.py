from pytgbot import Bot

API_KEY='2128132135:AAG8IhsdUS1MGwXwKRNeXQtQoNmCE9nLKxM'  # change this to the token you get from @BotFather
CHAT='2138683698'  # can be a @username or a id, change this to your own @username or id for example.

bot = Bot(API_KEY)

# sending messages:
bot.send_message(CHAT, "Example Text!")

# getting events:
for x in bot.get_updates():
	print(x)