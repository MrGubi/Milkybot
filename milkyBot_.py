from twitchio.ext import commands
from dotenv import load_dotenv
import datetime
import os
import yaml
import re
import sqlite3
import requests
import importlib
import openai
import random
import aiohttp
import asyncio
from commands import BotCommands  # Import the commands

# Load environment variables from .env file
load_dotenv()

def replace_invalid_unicode(text):
    return re.sub(r'\U000e0000', '', text)

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)
    

config = load_config()

conn = sqlite3.connect('chat_logs.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        username TEXT NOT NULL,
        content TEXT NOT NULL
    )
''')
conn.commit()

openai.api_key = os.getenv("OPENAI_API_KEY")
class Bot(commands.Bot):



    def __init__(self):
        token = os.getenv('OAUTH_TOKEN')
        botID = os.getenv('CLIENT_ID')
        user = os.getenv('BOT_USERNAME')
        channel = os.getenv('CHANNEL')
        super().__init__(token=token, prefix='!', nick=user, client_id=botID, initial_channels=[channel])
        self.global_cooldown = None

        # Add the commands cog
        self.add_cog(BotCommands(self))

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def is_streamer_live(self):
        channel = os.getenv('CHANNEL')
        contents = requests.get('https://www.twitch.tv/' + channel).content.decode('utf-8')

        if 'isLiveBroadcast' in contents:
            return True 
            print(channel + ' is live')
        else:
            print(channel + ' is not live')
            return False

    async def event_message(self, message):
        if message.author is None:
            return
        if message.author.name.lower() == self.nick.lower():
            return
        # check if streamer is live
        # if await self.is_streamer_live() == False:
        #     current_time = asyncio.get_event_loop().time()

        #     if self.global_cooldown and current_time < self.global_cooldown:
        #         remaining_time = round(self.global_cooldown - current_time, 2)
        #         print(f'Global cooldown active. Remaining time: {remaining_time} seconds')
        #         return
        #     await message.channel.send( "@"+message.author.name + " Unauthorized activity detected! Sending in the troops BOGGED")
        # else:
        #     return

        self.log_message_to_db(message.author.name, message.content)
        if message.author is None:
            return
        print(f'{message.author.name}: {message.content}')
        if message.author.name.lower() == "streamelements":
            await message.channel.send("@streamelements FuckYou")
        ran = random.randint(0,200)
        if ran == 1:
            await message.channel.send("hesGay")
        #if f"@{self.nick.lower()}" in message.content.lower():
            # Call OpenAI API and get a response
        #    response = await self.ask_openai(message.content)
        #    await message.channel.send(f"@{message.author.name} {response}")
        try:
            safe_to_message = message
            safe_to_message.content = replace_invalid_unicode(safe_to_message.content)
            await self.handle_commands(message)
        except:
            return
    

    def log_message_to_db(self, username, content):
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('INSERT INTO messages (date, username, content) VALUES (?, ?, ?)', (date, username, content))
        conn.commit()

    def get_top_chatters(self, top_n=3):
        c.execute('''
            SELECT username, COUNT(*) as count 
            FROM messages 
            GROUP BY username 
            ORDER BY count DESC 
            LIMIT ?
        ''', (top_n,))
        return c.fetchall()
    
    async def reload_commands(self):
        importlib.reload(commands)
        self.remove_cog('BotCommands')
        self.add_cog(BotCommands(self))
        print("BotCommands reloaded")

    async def ask_openai(self, user_message):
        try:
            response = openai.Completion.create(
                engine="gpt-3.5-turbo",  # You can change the engine based on your requirements
                messages=[
                {"role": "system", "content": "You are a normal chatter in milkys chat."},  # Optional system message to set behavior
                {"role": "user", "content": user_message}  # User's input
            ],
                max_tokens=100
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"Error with OpenAI: {e}")
            return
bot = None



def create_bot():
    global bot
    if bot is None:
        bot = Bot()

if __name__ == "__main__":
    create_bot()
    bot.run()