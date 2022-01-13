import discord
from discord.ext import commands
from discord.utils import get

from dotenv import load_dotenv

import asyncio
import os
import random

from commandVars import *

PREFIX = '.'
compMessageId = None

def main():
	bot = commands.Bot(
		command_prefix=PREFIX,
		help_command=None,
		case_insensitive=True,
		owner_id=(323860733798383617)
		)

	async def UpdateCompMessage(message):
		messageText = compMessageText
		emoji = bot.get_emoji(compEmojiId)

		reaction = get(message.reactions, emoji=emoji)

		if (reaction != None and reaction.count != 1):
			messageText += "\n\nThe current team comp consits of:\n"

			async for user in reaction.users():
				if user.id == bot.user.id: continue

				member = await message.guild.fetch_member(user.id)
				messageText += f"** - {member.mention}**\n"


		await message.edit(content=messageText)

	@bot.event
	async def on_ready():
		global compMessageId

		print(f"\"{bot.user.name}\" Has logged in!")

		# Set Discord Status
		await bot.change_presence(activity=discord.Game(name="with ur mother"))

		# Added Emoji To OW Comp Message
		compChannel = await bot.fetch_channel(compMessageChannelId)
		await compChannel.purge()

		compMessage = await compChannel.send("penis\n\n*(hehehehe)*")
		compMessageId = compMessage.id
		await UpdateCompMessage(compMessage)

		await compMessage.add_reaction(bot.get_emoji(compEmojiId))

	@bot.command()
	async def ping(ctx):
		await ctx.send(random.choice(pingMessages))

	@bot.command()
	async def say(ctx, *args):
		message = ""
		for arg in args:
			message += arg + " "

		await ctx.message.delete()
		await ctx.send(message)

	@bot.command()
	async def saychannel(ctx, channelId, *args):
		message = ""
		for arg in args:
			message += arg + " "

		channel = await bot.fetch_channel(channelId)

		await ctx.message.delete()
		await channel.send(message)

	@bot.command()
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

	@bot.command()
	async def help(ctx, cmd = None):
		def GetHelpMessage(cmd):
			cmdMessage = helpCommands[cmd.lower()]

			if (type(cmdMessage) == str):
				# No args supplied, so just print the description
				return f"**.{cmd.title()}** - {cmdMessage}"
			else:
				# Command has args, so make sure to print them
				return f"**.{cmd.title()} {cmdMessage[0]}** - {cmdMessage[1]}"

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

	@bot.command()
	async def compRemove(ctx, member : discord.Member, name="compRemove"):
	
		channel = await bot.fetch_channel(compMessageChannelId)
		message = await channel.fetch_message(compMessageId)
		emoji = bot.get_emoji(compEmojiId)
		author = ctx.message.author

		await ctx.message.delete(delay=5)
		if (member.id == bot.user.id):
			replyMsg = await ctx.channel.send(f"{author.mention} Dont even think bout it, bitch")
			await replyMsg.delete(delay=5) 
			return

		await message.remove_reaction(emoji, member)
		replyMsg = await ctx.channel.send(f"Removed {member.mention} from the comp")
		await replyMsg.delete(delay=5) 

	@bot.event
	async def on_raw_reaction_add(payload):
		if (payload.message_id != compMessageId): return

		channel = await bot.fetch_channel(payload.channel_id)
		user = await bot.fetch_user(payload.user_id)
		message = await channel.fetch_message(payload.message_id)
		reaction = get(message.reactions, emoji=payload.emoji)

		if (payload.emoji.id != compEmojiId or reaction.count > 7):
			await message.remove_reaction(payload.emoji, user)
		else:
			member = await message.guild.fetch_member(user.id)
			role = get(member.guild.roles, id=compRoleId)
			
			await member.add_roles(role)
			await UpdateCompMessage(message)

	@bot.event
	async def on_raw_reaction_remove(payload):
		if (payload.message_id != compMessageId): return

		user = await bot.fetch_user(payload.user_id)
		channel = await bot.fetch_channel(payload.channel_id)
		message = await channel.fetch_message(payload.message_id)
		member = await message.guild.fetch_member(user.id)
		role = get(member.guild.roles, id=compRoleId)
		
		await member.remove_roles(role)
		await UpdateCompMessage(message)

	@bot.event
	async def on_message(message):
		if message.author == bot.user:
			return

		if message.author.bot:
			return

		# Make sure this isnt a say command, cus then dubas will responed to the deleted message
		if message.content.lower().startswith(PREFIX + "say"):
			await bot.process_commands(message)
			return

		if f"<@!{bot.user.id}>" in message.content and not message.content.lower().startswith(PREFIX):
			ctx = await bot.get_context(message)
			await ctx.invoke(bot.get_command('ping'))

		for trigger in urMotherTriggers:
			if (trigger in message.content.lower().replace(" ", "")):
				await message.reply(random.choice(urMotherGifs))
				break

		# Dubas replay
		for role in message.author.roles:
			if role.id in dubasRoles:
				name = message.author.mention

				await message.reply(random.choice(dubasMessages).format(name))

		await bot.process_commands(message)

	# Start Bot
	load_dotenv()
	bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == '__main__':
	main()