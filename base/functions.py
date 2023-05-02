import discord
import asyncio

from discord import app_commands
from discord.ext import commands

from base import log, cfg

from typing import Union

async def error_delete_after(interaction, error):
    if  interaction.response.type == discord.InteractionResponseType.channel_message:
        return await interaction.response.send_message(
            content="%s você poderá usar este comando de novo." % format_dt(
                datetime.datetime.now() +
                datetime.timedelta(seconds=error.retry_after),
                'R'),
            delete_after=int(error.retry_after) - 1)

    elif interaction.response.type == discord.InteractionResponseType.deferred_message_update:
        return await interaction.followup.send(
            content="%s você poderá usar este comando de novo." % format_dt(
                datetime.datetime.now() +
                datetime.timedelta(seconds=error.retry_after),
                'R'),
            delete_after=int(error.retry_after) - 1)

async def report_error(self, error):
    log.exception(error)
    admin = self.bot.get_user(int(self.cfg.report_to))

    embed = discord.Embed(title="Relatório de erros", color=0xe01b24)
    embed.add_field(name=error.command.name, value=error.__cause__, inline=False)
    embed.set_footer(text=datetime.datetime.now())

    await admin.send(embed=embed)

async def cogs_manager(bot: commands.Bot, mode: str, cogs: list[str]) -> None:
    for cog in cogs:
        try:
            if mode == "unload":
                await bot.unload_extension(cog)
            elif mode == "load":
                await bot.load_extension(cog)
            elif mode == "reload":
                await bot.reload_extension(cog)
            else:
                raise ValueError("Invalid mode.")
            bot.log(f"Cog {cog} {mode}ed.", name="classes.utilities", level=logging.DEBUG)
        except Exception as e:
            raise e
def bot_has_permissions(**perms: bool):
    """A decorator that add specified permissions to Command.extras and add bot_has_permissions check to Command with specified permissions.
    
    Warning:
    - This decorator must be on the top of the decorator stack
    - This decorator is not compatible with commands.check()
    """
    def wrapped(command: Union[app_commands.Command, commands.HybridCommand, commands.Command]) -> Union[app_commands.Command, commands.HybridCommand, commands.Command]:
        if not isinstance(command, (app_commands.Command, commands.hybrid.HybridCommand, commands.Command)):
            raise TypeError(f"Cannot decorate a class that is not a subclass of Command, get: {type(command)} must be Command")

        valid_required_permissions = [
            perm for perm, value in perms.items() if getattr(discord.Permissions.none(), perm) != value
        ]
        command.extras.update({"bot_permissions": valid_required_permissions})

        if isinstance(command, commands.HybridCommand) and command.app_command:
            command.app_command.extras.update({"bot_permissions": valid_required_permissions})

        if isinstance(command, (app_commands.Command, commands.HybridCommand)):
            app_commands.checks.bot_has_permissions(**perms)(command)
        if isinstance(command, (commands.Command, commands.HybridCommand)):
            commands.bot_has_permissions(**perms)(command)

        return command

    return wrapped