import os
import random

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import load_dotenv

import google_api
import nlp
import clickup_api
from datetime import datetime, timezone

import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = int(os.getenv('GUILD_ID'))
GENERAL_CHANNEL = int(os.getenv('GENERAL_CHANNEL_ID'))
DEV_CHANNEL = int(os.getenv('DEV_CHANNEL_ID'))

PUPPY_DOC_ID = os.getenv('PUPPY_DOC_ID')
QUESTION_DOC = os.getenv('QUESTION_DOC_ID')
LINKS_DOC = os.getenv('LINKS_DOC_ID')
BOOKSHELF_DOC = os.getenv('BOOKSHELF_DOC_ID')
CONTENT_FOLDER = os.getenv('CONTENT_FOLDER_ID')

CLICKUP_TOKEN = os.getenv('CLICKUP_TOKEN')

@tasks.loop(hours=24)
async def post_daily_status(bot, id):
    channel = bot.get_channel(id)
    now = datetime.now(timezone.utc)
    msg = f'⏰⏰⏰Today is UTC Time {now.date()}⏰⏰⏰\n\n⬇️⬇️⬇️Here are our ongoing tasks⬇️⬇️⬇️\n'
    tasks = bot.clickup.get_tasks_by_date(now)
    msg += '\n'.join(tasks)
    msg += f'\n\n⬇️⬇️⬇️Here are our future tasks⬇️⬇️⬇️\n'
    future_tasks = bot.clickup.get_tasks_in_future(now)
    msg += '\n'.join(future_tasks)
    await channel.send('Your message')

class client(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.synced = False # the bot doesn't sync commands more than once
        self.clickup = clickup_api.MyClickUp(CLICKUP_TOKEN)
        self.mangas = [line.split(',') for line in google_api.get_raw_text_from_doc(BOOKSHELF_DOC).split('\n') if line != '']

    async def on_ready(self):
        await self.wait_until_ready()
        post_daily_status.start(self, GENERAL_CHANNEL)
        if not self.synced: # check if slash commands have been synced 
            await tree.sync(guild = discord.Object(id=GUILD))
            self.synced = True
        print(f"We have logged in as {self.user}.")

bot = client()
tree = app_commands.CommandTree(bot)

@tree.command(
    guild = discord.Object(id=GUILD), 
    name = 'about', 
    description='know about me'
)
async def post_about(interaction: discord.Interaction):
    msg = '''
🕸️🕸️🕸️
I'm Indra's Bot. I'm very knowledgable and I keep track of things.
I'm still under development. Feature request is welcome.
Check my source code here: https://github.com/ArielJiang0520/indras-net-internal-discord-bot
'''
    await interaction.response.send_message(msg) 

@tree.command(
    guild = discord.Object(id=GUILD), 
    name = 'puppy', 
    description='get a puppy picture to brighten your day!'
)
async def post_puppy(interaction: discord.Interaction):
    puppy_urls = [line for line in google_api.get_raw_text_from_doc(PUPPY_DOC_ID).split('\n') if line != '']
    picture = discord.Embed().set_image(url=random.choice(puppy_urls))
    await interaction.response.send_message(f"Here's a puppy!", embed=picture) 

@tree.command(
    guild = discord.Object(id=GUILD), 
    name = 'show-links', 
    description='show all the essential links'
)
async def show_link(interaction: discord.Interaction):
    links_doc = google_api.get_raw_text_from_doc(LINKS_DOC)
    await interaction.response.send_message(links_doc) 

@tree.command(
    guild = discord.Object(id=GUILD), 
    name = 'iterate-content', 
    description='iterate through our content folder and see what we have'
)
async def iterate_content(interaction: discord.Interaction):
    await interaction.response.defer()

    content_folder = google_api.iterate_content_folder(CONTENT_FOLDER)
    msg = '👋👋👋Thank you for waiting! Here are what I found in our /content Google Drive folder:\n'
    for folder, files in content_folder:
        msg += f'\n📃**{folder}**📃\n'
        for f in files:
            msg += f'\t{f[0]} {f[1]}\n'
    
    await interaction.followup.send(msg) 

@tree.command(
    guild = discord.Object(id=GUILD), 
    name = 'schedule-today', 
    description='check the schedule for today'
)
async def post_schedule_today(interaction: discord.Interaction):
    now = datetime.now(timezone.utc)
    msg = f'⏰⏰⏰Today is UTC Time {now.date()}⏰⏰⏰\n\n⬇️⬇️⬇️Here are our ongoing tasks⬇️⬇️⬇️\n'
    tasks = bot.clickup.get_tasks_by_date(now)
    msg += '\n'.join(tasks)
    msg += f'\n\n⬇️⬇️⬇️Here are our future tasks⬇️⬇️⬇️\n'
    future_tasks = bot.clickup.get_tasks_in_future(now)
    msg += '\n'.join(future_tasks)
    
    await interaction.response.send_message(msg) 

@tree.command(
    guild = discord.Object(id=GUILD), 
    name = 'schedule-by-person', 
    description='figure out someone\'s current and future schedule'
)
async def post_schedule_person(interaction: discord.Interaction, who: str):
    msg = f'🪄🪄🪄You searched for **{who.capitalize()}**🪄🪄🪄\n\n⬇️⬇️⬇️Here are the current and future tasks for them⬇️⬇️⬇️\n'
    tasks = bot.clickup.get_tasks_by_person(who.lower())
    msg += '\n'.join(tasks)
    
    await interaction.response.send_message(msg) 

@tree.command(
    guild = discord.Object(id=GUILD),
    name = 'search-wiki',
    description='search our wiki for a question you have'
)
async def search(interaction: discord.Interaction, keyword: str):
    await interaction.response.defer()

    question_doc = nlp.parse_doc(
        google_api.get_raw_text_from_doc(QUESTION_DOC)
    )
    answer = nlp.search_query(question_doc, keyword)
    res = ''
    for a in answer:
        res += '➡️' + a + '\n\n'
    msg = f'''
❓You asked about **"{keyword}"**❓
Here are the most related Q & A found in our 📖wiki📖:

{res}
Read more here: https://docs.google.com/document/d/1r1wlmZqziZQSFm3asJvbLQJMD1oGO0xe24_6UGfs-W4/edit#'''

    await interaction.followup.send(msg) 

@tree.command(
    guild = discord.Object(id=GUILD),
    name = 'bookshelf',
    description='search on the bookshelf to read a certain manga'
)
@app_commands.choices(
    choices=[app_commands.Choice(name=c[0], value=c[1]) for c in bot.mangas]
)
async def search(
    interaction: discord.Interaction, 
    choices: app_commands.Choice[str],
    chapter: int
):
    manga_dict = {c[1]:c[2] for c in bot.mangas}
    msg = f'''
🔍Found it!🔍 
Here's Chapter {chapter} of {choices.name}! Enjoy!🌟🌟🌟

Click Here ➡️➡️➡️ {manga_dict[choices.value].format(chapter=chapter)}
'''
    await interaction.response.send_message(msg)

asyncio.run(bot.start(TOKEN))