import discord
import os

from typing import Optional
from datetime import datetime
from discord.ext import commands
from discord.utils import format_dt

from base.functions import cogs_manager, bot_has_permissions

from os.path import dirname, abspath, join, basename, splitext
from sys import modules
from types import ModuleType

from base import log, cfg

from typing import Union

class Admin(commands.Cog, name="admin"):
	"""
		Admin commands.

		Require intents: 
			- message_content
		
		Require bot permission:
			- read_messages
			- send_messages
			- attach_files
	"""
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot


	@bot_has_permissions(send_messages=True)
	@commands.command(name="load")
	@commands.is_owner()
	async def load_cog(self, ctx: commands.Context, cog: str):
		"""Load a cog."""
		await cogs_manager(self.bot, "load", [f"cogs.{cog}"])
		await ctx.send(f":point_right: Cog {cog} loaded!")

	@bot_has_permissions(send_messages=True)
	@commands.command(name="unload")
	@commands.is_owner()
	async def unload_cog(self, ctx: commands.Context, cog: str):
		"""Unload a cog."""
		await cogs_manager(self.bot, "unload", [f"cogs.{cog}"])
		await ctx.send(f":point_left: Cog {cog} unloaded!")

	@bot_has_permissions(send_messages=True)
	@commands.command(name="reloadall", aliases=["rell"])
	@commands.is_owner()
	async def reload_all_cogs(self, ctx: commands.Context):
		"""Reload all cogs."""
		cogs = [cog for cog in self.bot.extensions]
		await cogs_manager(self.bot, "reload", cogs)	

		await ctx.send(f":muscle: All cogs reloaded: `{len(cogs)}`!")

	@bot_has_permissions(send_messages=True)
	@commands.command(name="reload", aliases=["rel"], require_var_positional=True)
	@commands.is_owner()
	async def reload_specified_cogs(self, ctx: commands.Context, *cogs: str):
		"""Reload specific cogs."""
		reload_cogs = [f"cogs.{cog}" for cog in cogs]
		await cogs_manager(self.bot, "reload", reload_cogs)

		await ctx.send(f":thumbsup: `{'` `'.join(cogs)}` reloaded!")

	@bot_has_permissions(send_messages=True)
	@commands.command(name="reloadlatest", aliases=["rl"])
	@commands.is_owner()
	async def reload_latest_cogs(self, ctx: commands.Context, n_cogs: int = 1):
		"""Reload the latest edited n cogs."""
		def sort_cogs(cogs_last_edit: list[list]) -> list[list]:
			return sorted(cogs_last_edit, reverse = True, key = lambda x: x[1])
		
		cogs = []
		for file in os.listdir(cogs_directory):
			actual = os.path.splitext(file)
			if actual[1] == ".py":
				file_path = os.path.join(cogs_directory, file)
				latest_edit = os.path.getmtime(file_path)
				cogs.append([actual[0], latest_edit])

		sorted_cogs = sort_cogs(cogs)
		reload_cogs = [f"cogs.{cog[0]}" for cog in sorted_cogs[:n_cogs]]
		await cogs_manager(self.bot, "reload", reload_cogs)

		await ctx.send(f":point_down: `{'` `'.join(reload_cogs)}` reloaded!")
		
	def reload_views():
		mods = [module[1] for module in modules.items() if isinstance(module[1], ModuleType)]
		for mod in mods:
			try:
				if basename(dirname(str(mod.__file__))) == "views":
					reload(mod)
					yield mod.__name__
			except: 
				pass

	@bot_has_permissions(send_messages=True)
	@commands.command(name="reloadviews", aliases=["rv"])
	@commands.is_owner()
	async def reload_view(self, ctx: commands.Context):
		"""Reload each registered views."""
		infants = self.reload_views()
		succes_text = f"👌 All views reloaded ! | 🔄 __`{sum(1 for _ in infants)} view(s) reloaded`__ : "
		for infant in infants: 
			succes_text += f"`{infant.replace('views.', '')}` "
		await ctx.send(succes_text)

	@bot_has_permissions(send_messages=True)
	@commands.command(name="synctree", aliases=["st"])
	@commands.is_owner()
	async def sync_tree(self, ctx: commands.Context, guild_id: Optional[str] = None):
		"""Sync application commands."""
		if guild_id:
			if guild_id == "guild" or guild_id == "~":
				guild_id = ctx.guild.id # type: ignore
			tree = await self.bot.tree.sync(guild=discord.Object(id=guild_id)) # type: ignore
		else:
			tree = await self.bot.tree.sync()

		log.info(
			message = f"{ctx.author} synced the tree({len(tree)}): {tree}",
			name = "discord.cogs.admin.sync_tree",
		)

		await ctx.send(f":pinched_fingers: `{len(tree)}` synced!")

	@bot_has_permissions(send_messages=True, attach_files=True)
	@commands.command(name="botlogs", aliases=["bl"])
	@commands.is_owner()
	async def show_bot_logs(self, ctx: commands.Context):
		"""Upload the bot logs"""
		logs_file = os.path.join('.', "kiniga.log")

		await ctx.send(file=discord.File(fp=logs_file, filename="bot.log"))

	@bot_has_permissions(send_messages=True)
	@commands.command(name="uptime")
	@commands.is_owner()
	async def show_uptime(self, ctx: commands.Context):
		"""Show the bot uptime."""
		uptime = datetime.now() - self.bot.uptime
		await ctx.send(f":clock1: {format_dt(self.bot.uptime, 'R')} ||`{uptime}`||")

	@bot_has_permissions(send_messages=True)
	@commands.command(name="shutdown")
	@commands.is_owner()
	async def shutdown_structure(self, ctx: commands.Context):
		"""Shutdown the bot."""
		await ctx.send(f":wave: `{self.bot.user.name}` is shutting down...") # type: ignore

		await self.bot.close()



async def setup(bot: commands.Bot):
	await bot.add_cog(Admin(bot))
