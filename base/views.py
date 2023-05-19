import discord

from discord.ext import commands

from typing import List, Union, Any, Callable, Coroutine, Optional

from discord.ui import View, Modal, TextInput, Button

from discord import ui, app_commands

class defaultViewButton(discord.ui.View):
    def __init__(self, timeout, checkrole:bool = False):
        super().__init__()
        self.timeout = timeout
        self.value = None
        self.bot = commands.Bot
        self.checkrole = checkrole

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.checkrole:
            assert await check_roles()
        await interaction.response.send_message('Confirmado.', ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.remove_buttons()
        await interaction.response.send_message('Cancelando...', ephemeral=True)
        self.value = False
        self.stop()

    def remove_buttons(self):
        for i in self.children:
            self.remove_item(i)

    async def check_roles(self, interaction):
        roles = [role.id for role in interaction.user.roles]
        roles_ = [ self.bot.config["config"]["eqp_role"] ]

        if has_roles := (set(roles) & set(roles_)):
            return True
        return False

    async def on_timeout(self, interaction: discord.Interaction):
        self.remove_buttons()

        await interaction.response.edit_message(view=self)
        self.stop()