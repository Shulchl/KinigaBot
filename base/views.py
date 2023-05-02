import discord

from typing import List, Union, Any, Callable, Coroutine, Optional

from discord.ui import View, Modal, TextInput, Button

from discord import ui, app_commands

class defaultViewButton(discord.ui.View):
    def __init__(self, timeout):
        super().__init__()
        self.timeout = timeout
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.remove_buttons()
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
            i.disabled = True

    async def on_timeout(self, interaction: discord.Interaction):
        self.remove_buttons()

        await interaction.response.edit_message(view=self)
        self.stop()