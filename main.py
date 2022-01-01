import discord

import os

from dotenv import load_dotenv


client = discord.Client()

dubasRoles = [
	893205641622085682,
	893208682588962846,
	893904856778158080,
	926796594882428938
]

helpMessage = {
	"help": "Displays this message"
}

def main():
	@client.event
	async def on_ready():
		print(f"\"{client.user.name}\" Has logged in!")

	@client.event
	async def on_message(message):
		if message.author == client.user:
			return

		if message.author.bot:
			return

		# Dubas replay
		for role in message.author.roles:
			if role.id in dubasRoles:
				name = message.author.nick
				if (name == None): name = message.author.name

				await message.reply(f'lol {name} is a dubas')

	# Start Bot
	load_dotenv()
	client.run(os.getenv("DISCORD_TOKEN"))

if __name__ == '__main__':
    main()