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

bot = commands.Bot(command_prefix='!',intents=intents)

def main():
    init_db()

main()

@bot.event
async def on_ready():
    print('We are alive.')

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

    add(species_msg.content,name_msg.content,int(interval_msg.content), watered_msg.content)
    await ctx.send(f'{name_msg.content} added!')


#### FUNCTION CALLS
#get_plant()
#plant_list()
#water_log()

bot.run(token)