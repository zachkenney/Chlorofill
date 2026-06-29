from dotenv import load_dotenv
from tabulate import tabulate
import logging
from db.database import *
import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import dateparser

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/',intents=intents)

def main():
    init_db()

main()

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        logging.info('Commands synced.')
    except Exception as e:
        logging.error(f'Sync failed: {e}')
    if not check_watering.is_running():
        check_watering.start()
        
class AddPlantModal(discord.ui.Modal, title='Add a Plant'):
    species = discord.ui.TextInput(label='Species')
    nickname = discord.ui.TextInput(label='Nickname')
    interval = discord.ui.TextInput(label='Watering interval (days)')
    last_watered = discord.ui.TextInput(label='Last watered (e.g. "YYYY-MM-DD")')

    async def on_submit(self, interaction: discord.Interaction):
        try:
            interval = int(self.interval.value)
        except ValueError:
            await interaction.response.send_message('Interval must be a whole number.', ephemeral=True)
            return
        parsed = dateparser.parse(self.last_watered.value)
        if parsed is None:
            await interaction.response.send_message('Unable to parse date. Try a different format.')
        last_watered_str = parsed.strftime('%Y-%m-%d')
        add(self.nickname.value.lower(), self.species.value, int(self.interval.value), last_watered_str)
        await interaction.response.send_message(f"{self.nickname.value.capitalize()} added!")    

@bot.tree.command()
async def add_plant(interaction: discord.Interaction):
    await interaction.response.send_modal(AddPlantModal())

@bot.tree.command()
async def get_plants(interaction: discord.Interaction):
    plants = find()
    table = tabulate([dict(p) for p in plants], headers='keys')
    await interaction.response.send_message(f'```{table}```')

@bot.tree.command()
async def watered(interaction: discord.Interaction, nickname:str):
    addlog(nickname.lower())
    await interaction.response.send_message(f'{nickname.lower()} watered!')

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

@bot.tree.command()
async def remove_plant(interaction: discord.Interaction, nickname:str):
    view = ConfirmDelete(nickname)
    await interaction.response.send_message(f'✋ Delete {nickname}, are you sure?', view=view)

@tasks.loop(hours=24)
async def check_watering():
    today = date.today().isoformat()
    plants = checkdate(today)
    channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))
    for plant in plants:
        await channel.send(f"🌱 {plant['name']} needs to be watered!")

@check_watering.before_loop
async def before_check_watering():
    await bot.wait_until_ready()

bot.run(token)