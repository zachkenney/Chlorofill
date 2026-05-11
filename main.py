from dotenv import load_dotenv
from tabulate import tabulate
import logging
from db.database import *
import discord
from discord.ext import commands
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
## eventually i want to switch to modals.
bot = commands.Bot(command_prefix='!',intents=intents)

def main():
    init_db()

main()

@bot.event
async def on_ready():
    print('We are alive.')

@task.loop(hours=24)
async def check_watering(ctx):
    today = date.today().isoformat()
    plants = checkdate(today)
    for plant in plants:
        await ctx.send(f'{plant['name']} needs to be watered.')

@bot.command()
async def add_plant(ctx):
    if ctx.channel.name != 'plants':
        await ctx.send('This command can only be used in #plants.')
        return
    await ctx.send('What species is your plant?')
    species_msg = await bot.wait_for('message', check= lambda m: m.author == ctx.author)

    await ctx.send('What\'s your plants nickname?')
    name_msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    await ctx.send('How often does this plant need to be watered? Numbers only please!')
    interval_msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    await ctx.send('When was the plant last watered?')
    watered_msg = await bot.wait_for('message', check=lambda m: m.author == ctx.author)

    add(name_msg.content,species_msg.content,int(interval_msg.content), watered_msg.content)
    await ctx.send(f'{name_msg.content} added!')

@bot.command()
async def get_plants(ctx):
    plants = find()
    for plant in plants:
        await ctx.send(f'{plant['name']} ({plant['species']}) wants to be watered every {plant['watering_interval_days']} days. Next watering date is {plant['next_date']}')

#### FUNCTION CALLS
#get_plant()
#plant_list()
#water_log()

bot.run(token)