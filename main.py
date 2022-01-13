import discord
from discord.ext import commands
from discord.member import Member
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

	def HasRole(member, roleId):
		role = discord.utils.find(lambda r: r.id == roleId, member.guild.roles)
		return role in member.roles

	def IsMod(member):
		return member.guild_permissions.administrator or HasRole(member, modRoleId)

	async def FailIfNotMod(ctx):
		if (not IsMod(ctx.author)):
			replyMsg = await ctx.channel.send(f"{ctx.author.mention} You need to be a Mod to run this command!")
			await replyMsg.delete(delay=3) 
			return True

		return False

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

	async def SayMessage(ctx, channelId, *args):
		message = ""
		for arg in args:
			message += arg + " "

		channel = await bot.fetch_channel(channelId)
		if (ctx.message.reference != None) and (ctx.message.reference.channel_id == channelId):
			messageReply = await channel.fetch_message(ctx.message.reference.message_id)
			await messageReply.reply(message)
		else:
			await channel.send(message)

		await ctx.message.delete()

	@bot.command()
	async def say(ctx, *args):
		await SayMessage(ctx, ctx.channel.id, *args)

	@bot.command()
	async def saychannel(ctx, channelId, *args):
		await SayMessage(ctx, channelId, *args)

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
	async def delete(ctx, amount):
		await ctx.message.delete()

		if await FailIfNotMod(ctx):
			return

		try:
			int(amount)
		except:
			replyMsg = await ctx.channel.send(f"Invalid Argument \"{amount}\" for **Amount**")
			await replyMsg.delete(delay=3)

		progressMsg = await ctx.channel.send(f"Deleting **{amount}** Messages...")
		def IsntProgressMsg(m): return m != progressMsg
		
		deleted = await ctx.channel.purge(limit=int(amount) + 1, check=IsntProgressMsg)
		await progressMsg.delete()

		replyMsg = await ctx.channel.send(f"Deleted **{len(deleted)}** Messages!")
		await replyMsg.delete(delay=3)


	@bot.command()
	async def compRemove(ctx, member : discord.Member):
		await ctx.message.delete(delay=3)

		if not HasRole(ctx.author, compPermsRoleId):
			replyMsg = await ctx.channel.send(f"{ctx.author.mention} You are not an Overwatch Gamer!")
			await replyMsg.delete(delay=3) 
			return

		if (member.id == bot.user.id):
			replyMsg = await ctx.channel.send(f"{ctx.author.mention} Dont even think bout it, bitch")
			await replyMsg.delete(delay=3) 
			return

		channel = await bot.fetch_channel(compMessageChannelId)
		message = await channel.fetch_message(compMessageId)
		emoji = bot.get_emoji(compEmojiId)

		await message.remove_reaction(emoji, member)
		replyMsg = await ctx.channel.send(f"Removed {member.mention} from the comp")
		await replyMsg.delete(delay=3) 

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