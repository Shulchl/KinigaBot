import discord

from discord.ext import commands
from discord import app_commands
from logging import ERROR as LOG_ERROR, CRITICAL as LOG_CRITICAL

from base.functions import log, cfg

class Errors(commands.Cog, name="errors"):
	"""Errors handler."""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot
		bot.tree.error(coro = self.__dispatch_to_app_command_handler)

		self.default_error_message = "֎・Ocorreu um erro."

	"""def help_custom(self):
		emoji = "<a:crossmark:842800737221607474>"
		label = "Error"
		description = "A custom errors handler. Nothing to see here."
		return emoji, label, description"""



	def trace_error(self, level: str, error: Exception):
		self.bot.log(
			msg = type(error).__name__,
			name = f"discord.{level}",
			level = LOG_ERROR,
			exc_info = error,
		)
		#await send_error_response(self, error)
		raise error

	async def __dispatch_to_app_command_handler(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
		self.bot.dispatch("app_command_error", interaction, error)

	async def __respond_to_interaction(self, interaction: discord.Interaction) -> bool:
		try:
			await interaction.response.send_message(content=self.default_error_message, ephemeral=True)
			return True
		except discord.errors.InteractionResponded:
			return False

	@commands.Cog.listener("on_error")
	async def get_error(self, event, *args, **kwargs):
		"""Error handler"""
		self.bot.log(
			message = f"Unexpected Internal Error: (event) {event}, (args) {args}, (kwargs) {kwargs}.",
			name = "discord.get_error",
			level = LOG_CRITICAL,
		)

	@commands.Cog.listener("on_command_error")
	async def get_command_error(self, ctx: commands.Context, error: commands.CommandError):
		"""Command Error handler
		doc: https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#exception-hierarchy
		"""
		try:
			if ctx.interaction: # HybridCommand Support
				await self.__respond_to_interaction(ctx.interaction)
				edit = ctx.interaction.edit_original_response
				if isinstance(error, commands.HybridCommandError):
					error = error.original # Access to the original error
			else:
				try:
					if isinstance(error, commands.RoleNotFound):
						return
					discord_message = await ctx.send(self.default_error_message)
				except discord.errors.Forbidden:
					self.trace_error("get_app_command_error", d_error)
					return
				edit = discord_message.edit
			raise error

		# ConversionError
		except commands.ConversionError as d_error:
			await edit(content=f"֎・{d_error}")
		# UserInputError
		except commands.MissingRequiredArgument as d_error:
			await edit(content=f"֎・Algo está faltando. `{ctx.clean_prefix}{ctx.command.name} <{'> <'.join(ctx.command.clean_params)}>`")
		# UserInputError -> BadArgument
		except commands.MemberNotFound or commands.UserNotFound as d_error:
			await edit(content=f"֎・Membro `{str(d_error).split(' ')[1]}` não encontrado ! Você pode pingar ele(a)!")
		# UserInputError -> BadUnionArgument | BadLiteralArgument | ArgumentParsingError
		except commands.BadArgument or commands.BadUnionArgument or commands.BadLiteralArgument or commands.ArgumentParsingError as d_error:
			await edit(content=f"֎・{d_error}")
		# CommandNotFound
		except commands.CommandNotFound as d_error:
			await edit(content=f"֎・Comando `{str(d_error).split(' ')[1]}` não encontrado!")
		# CheckFailure
		except commands.PrivateMessageOnly:
			await edit(content="֎・Esse comando não pode ser usado em servidores teste usá-lo do direct ;).")
		except commands.NoPrivateMessage:
			await edit(content="֎・isso não eestá funcionando como esperado.")
		except commands.NotOwner:
			await edit(content="֎・Você precisa ser dono do bot para poder usar esse comando.")
		except commands.MissingPermissions as d_error:
			await edit(content=f"֎・Você precisa das seguintes permissões: `{'` `'.join(d_error.missing_permissions)}`.")
		except commands.BotMissingPermissions as d_error:
			if not "send_messages" in d_error.missing_permissions:
				await edit(content=f"֎・O bot precisa das seguintes permissões: `{'` `'.join(d_error.missing_permissions)}`.")
		except commands.CheckAnyFailure or commands.MissingRole or commands.BotMissingRole or commands.MissingAnyRole or commands.BotMissingAnyRole as d_error:
			await edit(content=f"֎・{d_error}")
		except commands.NSFWChannelRequired:
			await edit(content="֎・Esse comando precisa ser usado em um comando NSFW.")
		# DisabledCommand
		except commands.DisabledCommand:
			await edit(content="֎・Foi mal, mas esse comando está desabilitado.")
		# CommandInvokeError
		except commands.CommandInvokeError as d_error:
			await edit(content=f"֎・{d_error.original}")
		# CommandOnCooldown
		except commands.CommandOnCooldown as d_error:
			await edit(content=f"֎・Comando em cooldown, espere `{str(d_error).split(' ')[7]}` !")
		# MaxConcurrencyReached
		except commands.MaxConcurrencyReached as d_error:
			await edit(content=f"֎・Parece que você atingiu o limite. Número máximo de invocações simultâneas permitidas: `{d_error.number}`, por `{d_error.per}`.")
		# HybridCommandError
		except commands.HybridCommandError as d_error:
			await self.get_app_command_error(ctx.interaction, error)
		except Exception as e:
			self.trace_error("get_command_error", e)

	@commands.Cog.listener("on_app_command_error")
	async def get_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
		"""App command Error Handler
		doc: https://discordpy.readthedocs.io/en/latest/interactions/api.html#exception-hierarchy
		"""
		try:
			await self.__respond_to_interaction(interaction)
			edit = interaction.edit_original_response

			raise error
		except app_commands.CommandInvokeError as d_error:
			if isinstance(d_error.original, discord.errors.InteractionResponded):
				await edit(content=f"֎・{d_error.original}")
			elif isinstance(d_error.original, discord.errors.Forbidden):
				await edit(content=f"֎・`{type(d_error.original).__name__}` : {d_error.original.text}")
			else:
				await edit(content=f"֎・`{type(d_error.original).__name__}` : {d_error.original}")

			self.trace_error("get_app_command_error", d_error)
		except app_commands.CheckFailure as d_error:
			if isinstance(d_error, app_commands.errors.CommandOnCooldown):
				await edit(content=f"֎・Comando em cooldown, espere `{str(d_error).split(' ')[7]}` !")
			else:
				await edit(content=f"֎・`{type(d_error).__name__}` : {d_error}")

			self.trace_error("get_app_command_error", d_error)
		except app_commands.CommandNotFound:
			await edit(content=f"֎・Comando não encontrado. parece ser um bug do discord, provavelmente por não estar sincronizado.\nTalvez tenha vários comandos com o mesmo nome. Tente outro comando.")
		except Exception as e: 
			"""
			Caught here:
			app_commands.TransformerError
			app_commands.CommandLimitReached
			app_commands.CommandAlreadyRegistered
			app_commands.CommandSignatureMismatch
			"""

			self.trace_error("get_app_command_error", e)

	@commands.Cog.listener("on_view_error")
	async def get_view_error(self, interaction: discord.Interaction, error: Exception, item: any):
		"""View Error Handler"""
		try:
			raise error
		except discord.errors.Forbidden:
			pass
		except Exception as e:
			self.trace_error("get_view_error", e)

	@commands.Cog.listener("on_modal_error")
	async def get_modal_error(self, interaction: discord.Interaction, error: Exception):
		"""Modal Error Handler"""
		try:
			raise error
		except discord.errors.Forbidden:
			pass
		except Exception as e:
			self.trace_error("get_modal_error", e)

async def setup(bot: commands.Bot):
	await bot.add_cog(Errors(bot))