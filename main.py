import discord
from discord.ext import commands

from dotenv import load_dotenv

import asyncio
import os
import random

from commandVars import *

PREFIX = '.'

def main():
	client = commands.Bot(
		command_prefix=PREFIX,
		help_command=None,
		case_insensitive=True,
		owner_id=(323860733798383617)
		)

	@client.event
	async def on_ready():
		print(f"\"{client.user.name}\" Has logged in!")
		await client.change_presence(activity=discord.Game(name="with ur mother"))

	@client.command()
	async def ping(ctx):
		await ctx.send(random.choice(pingMessages))

	@client.command()
	async def say(ctx, *args):
		message = ""
		for arg in args:
			message += arg + " "

		await ctx.message.delete()
		await ctx.send(message)

	@client.command()
	async def joke(ctx):
		jokeMessage = await ctx.send(random.choice(jokes))
		await asyncio.sleep(3)
		latestMessage = await jokeMessage.channel.fetch_message(jokeMessage.channel.last_message_id)

		if (jokeMessage == latestMessage):
			# Last message sent was the joke, no need to reply
			await ctx.send("ur mother")
		else:
			# There have been new messages since the joke was made, so reply to it
			await jokeMessage.reply("ur mother")

	@client.command()
	async def help(ctx, cmd = None):
		def GetHelpMessage(cmd):
			cmdMessage = helpCommands[cmd.lower()]

			if (type(cmdMessage) == str):
				# No args supplied, so just print the description
				return f"**{cmd.title()}** - {cmdMessage}"
			else:
				# Command has args, so make sure to print them
				return f"**{cmd.title()} {cmdMessage[0]}** - {cmdMessage[1]}"

		if (cmd == None):
			# Specific command not specified, so list all commands

			helpMessage = ""
			for cmd in helpCommands:
				helpMessage += GetHelpMessage(cmd) + '\n'

			await ctx.send(helpMessage)
		else:
			# Specific command specified, so print it

			cmd = cmd.lower()

			if not (cmd in helpCommands):
				await ctx.send(f"Command **\"{cmd.title()}\"** not found!")
				return

			await ctx.send(GetHelpMessage(cmd))

	@client.event
	async def on_message(message):
		if message.author == client.user:
			return

		if message.author.bot:
			return

		# Make sure this isnt a say command, cus then dubas will responed to the deleted message
		if message.content.lower().startswith(PREFIX + "say"):
			await client.process_commands(message)
			return

		if client.user.mentioned_in(message):
			ctx = await client.get_context(message)
			await ctx.invoke(client.get_command('ping'))

		# Dubas replay
		for role in message.author.roles:
			if role.id in dubasRoles:
				name = message.author.nick
				if (name == None): name = message.author.mention

				await message.reply(random.choice(dubasMessages).format(name))

		await client.process_commands(message)

	# Start Bot
	load_dotenv()
	client.run(os.getenv("DISCORD_TOKEN"))

if __name__ == '__main__':
	main()