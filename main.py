from dotenv import load_dotenv
from tabulate import tabulate
import logging
from db.database import *
import discord
from discord import app_commands
from discord.ext import commands, tasks
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
guild = int(os.getenv('GUILD_ID')) # clean this up once done to make it global.
channel = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/',intents=intents)
MY_GUILD = discord.Object(id=guild)

def main():
    init_db()

main()

@bot.event
async def on_ready():
    check_watering.start()
    await bot.tree.sync(guild=discord.Object(id=guild))  # syncs guild commands
    print('Commands synced.')

class AddPlantModal(discord.ui.Modal, title='Add a Plant'):
    species = discord.ui.TextInput(label='Species')
    nickname = discord.ui.TextInput(label='Nickname')
    interval = discord.ui.TextInput(label='Watering interval (days)')
    last_watered = discord.ui.TextInput(label='Last watered (YYYY-MM-DD)')

    async def on_submit(self, interaction: discord.Interaction):
        add(self.nickname.value, self.species.value, int(self.interval.value), self.last_watered.value)
        await interaction.response.send_message(f"{self.nickname.value} added!")    

@bot.tree.command(guild=MY_GUILD)
async def add_plant(interaction: discord.Interaction):
    await interaction.response.send_modal(AddPlantModal())

@bot.tree.command(guild=MY_GUILD)
async def get_plants(interaction: discord.Interaction):
    plants = find()
    table = tabulate([dict(p) for p in plants], headers='keys')
    await interaction.response.send_message(f'```{table}```')

@bot.tree.command(guild=MY_GUILD)
async def watered(interaction: discord.Interaction, nickname:str):
    addlog(nickname)
    await interaction.response.send_message(f'{nickname} watered!')

class ConfirmDelete(discord.ui.View):
    def __init__(self, nickname):
        super().__init__()
        self.nickname = nickname

    @discord.ui.button(label='Yes', style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        delete(self.nickname)
        await interaction.response.send_message(f'{self.nickname} deleted.')

    @discord.ui.button(label='No', style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelled.')

@bot.tree.command(guild=MY_GUILD)
async def remove_plant(interaction: discord.Interaction, nickname:str):
    view = ConfirmDelete(nickname)
    await interaction.response.send_message(f'Delete {nickname}, are you sure?', view=view)

@tasks.loop(hours=24)
async def check_watering():
    today = date.today().isoformat()
    plants = checkdate(today)
    channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))
    for plant in plants:
        await channel.send(f"{plant['name']} needs to be watered!")

bot.run(token)