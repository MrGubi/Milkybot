from twitchio.ext import commands
import datetime
import json
import random
import re
import asyncio
import os

def replace_invalid_unicode(text):
    return re.sub(r'\U000e0000', '', text)

class BotCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # Load quotes and hate dictionaries
        if os.path.exists('quotes.json') and os.path.getsize('quotes.json') > 0:
            self.Quotes = json.load(open('quotes.json'))
        else:
            self.Quotes = {}
        if os.path.exists('hate.json') and os.path.getsize('hate.json') > 0:
            self.Hate = json.load(open('hate.json'))
        else:
            self.Hate = {}

    @commands.command(name='quote')
    async def quote(self, ctx, user_name: str = None, index: int = None, *args):
        if user_name is not None:
            if user_name[0] == '@':
                user_name = user_name[1:].lower()
            else:
                user_name = re.sub(r'[^\w\s]', '', user_name).lower()

        if not self.Quotes:
            await ctx.send("No quotes available.")
            return
       
        if user_name is not None and user_name != '':
            quotes_by_user = [quote for quote in self.Quotes.values() if quote['user'] == user_name]
            if not quotes_by_user:
                await ctx.send(f"No quotes found for user {user_name}.")
                return
            else:
                if index is not None:
                    try:
                        selected_quote = quotes_by_user[index - 1]
                    except:
                        await ctx.send(f"No quote found at index {index} for user {user_name}.")
                else:
                    selected_quote = random.choice(quotes_by_user)
                await ctx.send(f'/me {selected_quote["quote"]} - @{selected_quote["user"]}, {selected_quote["date"]} ')
                return

        selected_quote = random.choice(list(self.Quotes.values()))

        await ctx.send(f'/me {selected_quote["quote"]} - @{selected_quote["user"]}, {selected_quote["date"]} ')
    
    @commands.command(name='addquote')
    async def addquote(self, ctx):
        if not ctx.author.is_mod:
            return
        # Extract the quote and user name from the message content
        parts = ctx.message.content.split(' ', 2)
        if len(parts) < 3:
            await ctx.send('Usage: !addquote <user_name> <quote>')
            return

        user_name = parts[1]
        #if username first letter is @ remove it
        if user_name[0] == '@':
            user_name = user_name[1:]
        quote = parts[2]
        user_name = user_name.lower()
        # Get the current date and time
        now = datetime.datetime.now()
        date_str = now.strftime("%d-%m-%Y")

        # Add the quote along with the user name and date to the quotes dictionary
        quote_id = len(self.Quotes) + 1
        self.Quotes[quote_id] = {
            'user': user_name,
            'quote': quote,
            'date': date_str
        }

        # Save the updated quotes to the JSON file
        try:
            with open('quotes.json', 'w') as f:
                json.dump(self.Quotes, f, indent=4)
            await ctx.send('Quote added')
        except IOError:
            await ctx.send('Failed to save the quote, please try again.')

    @commands.command(name='hate')
    async def hate(self, ctx, index: int = None, *args):
        if not self.Hate:
            await ctx.send("No hateful comments available.")
            return
        hateful_comment = random.choice(list(self.Hate.values()))
        await ctx.send(f"/me {hateful_comment['hate_comment']}")

    @commands.command(name='addhate')
    async def addhate(self, ctx):

        # Check if the user is a moderator
        if not ctx.author.is_mod:
            return
        # Extract the hateful comment from the message content
        parts = ctx.message.content.split(' ', 1)
        if len(parts) < 2:
            await ctx.send('Usage: !addhate <hateful_comment>')
            return

        hateful_comment = parts[1]

        # Add the hateful comment to the hate list
        hate_id = len(self.Hate) + 1
        self.Hate[hate_id] = {
            'hate_comment': hateful_comment
        }

        # Save the updated hate list to the JSON file
        try:
            with open('hate.json', 'w') as f:
                json.dump(self.Hate, f, indent=4)
            await ctx.send('Hateful comment added')
        except IOError:
            await ctx.send('Failed to save the hateful comment, please try again.')

    @commands.command(name='fish') 
    async def fish(self, ctx, *args):
        text = ' '.join(args)
        current_time = asyncio.get_event_loop().time()

        # Check global cooldown
        if self.bot.global_cooldown and current_time < self.bot.global_cooldown:
            remaining_time = round(self.bot.global_cooldown - current_time, 2)
            print(f'Global cooldown active. Remaining time: {remaining_time} seconds')
            return
        await ctx.send('!fish aga')
        # Set global cooldown
        self.bot.global_cooldown = current_time + 120  # 120 seconds cooldown


    @commands.command(name='alicebug') 
    async def alicebug(self, ctx, *args):
        await ctx.send('poor Trazerone36')

    @commands.command(name='botstats') 
    async def botstats(self, ctx, *args):
        await ctx.send('!stats')

    @commands.command(name='report') 
    async def report(self, ctx, name: str = None):
        await ctx.send(str(name) +' was reported for being a bad person.')
    

    @commands.command(name='shit') 
    async def shit(self, ctx, *args):
        await ctx.send('https://docs.google.com/spreadsheets/d/11OQFzt_4awmWaUDlgEY7_rAXD2EBfDSesPKU4HGZFOc/edit?usp=sharing')

    async def write_to_chat(self, message):
        await self.bot.get_channel(os.getenv('CHANNEL')).send(f'{message}')

    def add_new_command(self, name, func):
        self.add_command(commands.Command(name=name, func=func))


    @commands.command(name='reload')
    async def reload(self, ctx):
        if ctx.author.is_mod:
            await self.bot.reload_commands()
            await ctx.send("Commands reloaded successfully.")
        else:
            await ctx.send("You do not have permission to reload commands.")


    @commands.command(name='starter')
    async def reload(self, ctx):
        await ctx.send("Ask fub: https://www.twitch.tv/fubgun")