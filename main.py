import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import discord.utils
import random
import time
import asyncio
from datetime import datetime
import aiohttp
import imageio
from PIL import Image, ImageSequence
import io
import wikipedia
from discord.ui import View, Button
import logging
import os
from keep_alive import keep_alive

start_time = datetime.utcnow()

logging.basicConfig(level=logging.INFO)

welcome_channel_id = {}

warnings = {}

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.dm_messages = True
intents.voice_states = True

bot = commands.Bot(command_prefix=',', intents=intents)

SUSPICIOUS_ACCOUNT_AGE_DAYS = 7

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Successfully synced {len(synced)} slash command(s).')
    except Exception as e:
        print(f'Error syncing commands: {e}')

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    await interaction.response.send_message(f"An error occurred: {str(error)}", ephemeral=True)
    print(f"Error in {interaction.command.name}: {str(error)}")



@bot.tree.command(name='gif', description='Converts an uploaded image to a GIF and sends it')
async def gif_slash(interaction: discord.Interaction, image: discord.Attachment):
    await interaction.response.defer()

    try:
        if not image.content_type.startswith('image/'):
            await interaction.followup.send("Please upload a valid image file.")
            return

        image_data = io.BytesIO(await image.read())
        uploaded_image = Image.open(image_data)

        gif_buffer = io.BytesIO()
        frames = [frame.copy() for frame in ImageSequence.Iterator(uploaded_image)]
        frames[0].save(
            gif_buffer,
            format="GIF",
            save_all=True,
            append_images=frames[1:],
            loop=0,
            duration=100
        )
        gif_buffer.seek(0)

        await interaction.followup.send("Here's your GIF!", file=discord.File(gif_buffer, "output.gif"))

    except Exception as e:
        await interaction.followup.send(f"An error occurred: {str(e)}")
        
@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from bots

    if bot.user in message.mentions:
        embed = discord.Embed(
            title="Hello, I am at your assistance!",
            description=(
                "Thank you for mentioning me! Here are some ways I can help you:\n\n"
                "🔹 Use `,help` to see a list of commands I can perform.\n"
                "🔹 Run `,setup` for a step-by-step guide on configuring me for your server.\n"
                "🔹 Have questions? Just mention me, and I'll point you in the right direction.\n\n"
                "I'm here to assist with moderation, fun, utility, and much more!"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Ready to help you manage your server efficiently!")
        await message.channel.send(embed=embed)

    await bot.process_commands(message)


@bot.tree.command(name='8ball', description='Magic 8-ball response to your question')
async def eightball_slash(interaction: discord.Interaction, question: str):
    responses = ["Yes, definitely!", "No, not in a million years.", "Ask again later.", "It is certain.", "My sources say no."]
    await interaction.response.send_message(f"🎱 Question: {question}\nAnswer: {random.choice(responses)}")

@bot.tree.command(name='joke', description='Sends a random joke')
async def joke_slash(interaction: discord.Interaction):
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "What do you call fake spaghetti? An impasta!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!"
    ]
    await interaction.response.send_message(random.choice(jokes))

@bot.tree.command(name='quote', description='Sends a random inspirational quote')
async def quote_slash(interaction: discord.Interaction):
    quotes = [
        "The only limit to our realization of tomorrow is our doubts of today. – Franklin D. Roosevelt",
        "Do not watch the clock. Do what it does. Keep going. – Sam Levenson",
        "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt"
    ]
    await interaction.response.send_message(random.choice(quotes))

@bot.tree.command(name='cat', description='Sends a random cat image')
async def cat_slash(interaction: discord.Interaction):
    cat_images = ["https://placekitten.com/400/300", "https://placekitten.com/500/500"]
    await interaction.response.send_message(random.choice(cat_images))

@bot.tree.command(name='dog', description='Sends a random dog image')
async def dog_slash(interaction: discord.Interaction):
    dog_images = ["https://placedog.net/400/300", "https://placedog.net/500/500"]
    await interaction.response.send_message(random.choice(dog_images))

@bot.tree.command(name='coinflip', description='Flips a coin')
async def coinflip_slash(interaction: discord.Interaction):
    outcome = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 The coin landed on **{outcome}**.")

@bot.tree.command(name='motivate', description='Sends a motivational quote')
async def motivate_slash(interaction: discord.Interaction):
    quotes = [
        "Believe you can and you're halfway there. – Theodore Roosevelt",
        "The only way to do great work is to love what you do. – Steve Jobs",
        "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill"
    ]
    await interaction.response.send_message(random.choice(quotes))

@bot.tree.command(name='trivia', description='Sends a random trivia question')
async def trivia_slash(interaction: discord.Interaction):
    questions = [
        ("What is the capital of France?", "Paris"),
        ("How many continents are there?", "7"),
        ("Who wrote 'Hamlet'?", "Shakespeare")
    ]
    question, answer = random.choice(questions)
    await interaction.response.send_message(f"❓ {question}")

    def check(m):
        return m.channel == interaction.channel and m.author == interaction.user

    try:
        user_response = await bot.wait_for('message', timeout=15.0, check=check)
        if user_response.content.lower() == answer.lower():
            await interaction.followup.send("✅ Correct!")
        else:
            await interaction.followup.send(f"❌ Incorrect. The correct answer was **{answer}**.")
    except asyncio.TimeoutError:
        await interaction.followup.send(f"⏳ Time's up! The correct answer was **{answer}**.")



@bot.command(name='setup')
async def setup_command(ctx):
    embed = discord.Embed(
        title="Bot Setup Guide",
        description=(
            "Follow this guide to set up the bot and ensure it runs smoothly:\n\n"
            "**Step 1: Permissions Check**\n"
            "Ensure the bot has the following permissions:\n"
            "🔹 Manage Roles\n"
            "🔹 Manage Channels\n"
            "🔹 Kick Members\n"
            "🔹 Ban Members\n"
            "🔹 Manage Messages\n"
            "🔹 Send Messages\n"
            "🔹 Read Message History\n"
            "🔹 Use Slash Commands\n"
            "🔹 Add Reactions\n"
            "\nRun `,checkbot` to check if the bot has the necessary permissions and ensure all commands work.\n\n"
            "**Step 2: Basic Configuration**\n"
            "1. **Set Join/Leave Channel**: Run `,setjoin <channel_id>` to set the channel where join/leave messages will be sent.\n"
            "2. **Verify Roles**: Ensure the bot has a higher role than the members it needs to manage.\n\n"
            "**Step 3: Testing Commands**\n"
            "Try using some basic commands, such as `,ping`, `,botinfo`, and `,userinfo`, to verify that the bot responds correctly.\n\n"
            "**Step 4: Admin and Utility Commands**\n"
            "Make sure you and other trusted users have the required permissions to run admin and utility commands like `,purge`, `,announce`, and `,slowmode`.\n\n"
            "**Step 5: Customize Settings**\n"
            "Adjust any other settings or run custom commands as needed to fit your server's requirements.\n\n"
            "If you run into any issues or need help, feel free to contact the support team or visit our community server."
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="Thank you for using the bot! Follow this guide for a smooth setup experience.")
    await ctx.send(embed=embed)

    await ctx.invoke(bot.get_command('checkbot'))


@bot.command(name='weather')
async def weather_command(ctx, *, city: str):
    api_key = 'YOUR_OPENWEATHERMAP_API_KEY'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                weather = data['weather'][0]['description']
                temperature = data['main']['temp']
                embed = discord.Embed(
                    title=f"Weather in {city.capitalize()}",
                    description=f"Condition: {weather.capitalize()}\nTemperature: {temperature}°C",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("City not found or there was an error retrieving the weather.")

@bot.command(name='checkbot')
async def checkbot_command(ctx):
    embed = discord.Embed(
        title="Bot Status Check",
        description="Checking the bot's status, permissions, and command functionality...",
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=embed)
    
    try:
        embed.add_field(name="Bot Status", value="🟢 Online", inline=False)
        
        required_permissions = [
            'send_messages', 'manage_messages', 'kick_members',
            'ban_members', 'manage_channels', 'moderate_members'
        ]
        bot_permissions = ctx.channel.permissions_for(ctx.guild.me)
        missing_permissions = [perm for perm in required_permissions if not getattr(bot_permissions, perm)]
        
        if missing_permissions:
            embed.add_field(
                name="Permissions",
                value=f"⚠️ Missing permissions: {', '.join(missing_permissions)}",
                inline=False
            )
        else:
            embed.add_field(name="Permissions", value="✅ All required permissions granted", inline=False)
        
        try:
            await ping_command(ctx)
            embed.add_field(name="Command Test", value="✅ Commands are functional", inline=False)
        except Exception as e:
            embed.add_field(name="Command Test", value=f"❌ Commands ran into an error: {str(e)}", inline=False)

        embed.color = discord.Color.green()
        embed.set_footer(text="Bot status check completed successfully.")
        await message.edit(embed=embed)
    
    except Exception as e:
        embed.add_field(name="Error", value=f"❌ An error occurred: {str(e)}", inline=False)
        embed.color = discord.Color.red()
        await message.edit(embed=embed)


@bot.command(name='urban')
async def urban_command(ctx, *, term: str):
    url = f'https://api.urbandictionary.com/v0/define?term={term}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                if data['list']:
                    definition = data['list'][0]['definition']
                    embed = discord.Embed(
                        title=f"Urban Dictionary: {term}",
                        description=definition,
                        color=discord.Color.orange()
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("No definition found for that term.")
            else:
                await ctx.send("There was an error retrieving the definition.")

@bot.command(name='roll')
async def roll_command(ctx, sides: int = 6):
    if sides < 2:
        await ctx.send("Please use a dice with at least 2 sides.")
    else:
        result = random.randint(1, sides)
        await ctx.send(f"🎲 You rolled a **{result}** on a {sides}-sided dice.")

@bot.command(name='motivate')
async def motivate_command(ctx):
    quotes = [
        "Believe you can and you're halfway there. – Theodore Roosevelt",
        "The only way to do great work is to love what you do. – Steve Jobs",
        "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill"
    ]
    await ctx.send(random.choice(quotes))

@bot.command(name='countdown')
async def countdown_command(ctx, seconds: int):
    if seconds > 3600:
        await ctx.send("The countdown limit is 3600 seconds (1 hour).")
        return
    await ctx.send(f"Starting countdown for {seconds} seconds...")
    while seconds:
        minutes, secs = divmod(seconds, 60)
        time_format = f"{minutes:02}:{secs:02}"
        await ctx.send(time_format)
        await asyncio.sleep(1)
        seconds -= 1
    await ctx.send("⏰ Time's up!")

@bot.command(name='leaderboard')
async def leaderboard_command(ctx):
    embed = discord.Embed(
        title="Server Leaderboard",
        description="Feature coming soon! Stay tuned for updates.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name='compliment')
async def compliment_command(ctx, member: discord.Member = None):
    member = member or ctx.author
    compliments = [
        "You're an amazing person!",
        "Your positivity is infectious!",
        "You light up the room!"
    ]
    await ctx.send(f"{member.mention}, {random.choice(compliments)}")

@bot.command(name='lock')
@commands.has_permissions(manage_channels=True)
async def lock_command(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"{ctx.channel.mention} has been locked.")

@bot.command(name='unlock')
@commands.has_permissions(manage_channels=True)
async def unlock_command(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"{ctx.channel.mention} has been unlocked.")

@bot.command(name='purge')
@commands.has_permissions(manage_messages=True)
async def purge_command(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)

@bot.command(name='userinfo')
async def userinfo_command(ctx, member: discord.Member):
    embed = discord.Embed(title=f"User Info - {member}", color=discord.Color.blue())
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Name", value=member.display_name, inline=True)
    embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles if role != ctx.guild.default_role]), inline=False)
    await ctx.send(embed=embed)

@bot.command(name='say')
@commands.has_permissions(administrator=True)
async def say_command(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

@bot.tree.command(name='say', description='Makes the bot say something')
@app_commands.checks.has_permissions(administrator=True)
async def say_slash_command(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message, ephemeral=False)


@bot.command(name='setjoin')
@commands.has_permissions(administrator=True)
async def setjoin_command(ctx, channel_id: int):
    global welcome_channel_id
    welcome_channel_id[ctx.guild.id] = channel_id
    channel = bot.get_channel(channel_id)
    if channel:
        await ctx.send(f"Welcome and leave messages will now be sent to {channel.mention}.")
    else:
        await ctx.send("Invalid channel ID. Please provide a valid channel ID.")

@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    if guild_id in welcome_channel_id:
        channel = member.guild.get_channel(welcome_channel_id[guild_id])
        if channel:
            embed = discord.Embed(
                title="Welcome!",
                description=f"{member.mention} has joined the server!",
                color=discord.Color.green()
            )
            embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC"), inline=False)
            embed.add_field(name="Total Members", value=f"{member.guild.member_count}", inline=False)
            await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    guild_id = member.guild.id
    if guild_id in welcome_channel_id:
        channel = member.guild.get_channel(welcome_channel_id[guild_id])
        if channel:
            embed = discord.Embed(
                title="Goodbye!",
                description=f"{member.mention} has left the server.",
                color=discord.Color.red()
            )
            embed.add_field(name="Total Members", value=f"{member.guild.member_count}", inline=False)
            await channel.send(embed=embed)

@bot.command(name='mute')
@commands.has_permissions(manage_roles=True)
async def mute_command(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)
    await member.add_roles(muted_role)
    await ctx.send(f"{member.mention} has been muted.")

@bot.command(name='unmute')
@commands.has_permissions(manage_roles=True)
async def unmute_command(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} has been unmuted.")
    else:
        await ctx.send(f"{member.mention} is not muted.")

@bot.command(name='serverinfo')
async def serverinfo_command(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"Server Info - {guild.name}", color=discord.Color.purple())
    embed.add_field(name="Owner", value=guild.owner, inline=True)
    embed.add_field(name="Server ID", value=guild.id, inline=True)
    embed.add_field(name="Member Count", value=guild.member_count, inline=True)
    embed.add_field(name="Created At", value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
    await ctx.send(embed=embed)

@bot.command(name='roleinfo')
async def roleinfo_command(ctx, role: discord.Role):
    embed = discord.Embed(title=f"Role Info - {role.name}", color=role.color)
    embed.add_field(name="ID", value=role.id, inline=True)
    embed.add_field(name="Color", value=str(role.color), inline=True)
    embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
    embed.add_field(name="Position", value=role.position, inline=True)
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    latency = bot.latency * 1000
    await ctx.send(f'🏓 Pong! Latency is {latency:.2f} ms.')

@bot.command(name='botinfo')
async def botinfo_command(ctx):
    embed = discord.Embed(title="Bot Info", color=discord.Color.gold())
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Created By", value="Polar", inline=True)
    embed.add_field(name="Uptime", value=str(datetime.utcnow() - start_time).split('.')[0], inline=True)
    await ctx.send(embed=embed)

@bot.command(name='uptime')
async def uptime_command(ctx):
    current_time = datetime.utcnow()
    uptime = current_time - start_time
    await ctx.send(f'🕒 Uptime: {str(uptime).split(".")[0]}')

@bot.command(name='slowmode')
@commands.has_permissions(manage_channels=True)
async def slowmode_command(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"⏳ Slowmode set to {seconds} seconds in {ctx.channel.mention}.")

@bot.command(name='clearwarns')
@commands.has_permissions(manage_messages=True)
async def clearwarns_command(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    member_id = member.id
    if guild_id in warnings and member_id in warnings[guild_id]:
        warnings[guild_id][member_id] = 0
        await ctx.send(f"Warnings for {member.mention} have been cleared.")
    else:
        await ctx.send(f"{member.mention} has no warnings.")

@bot.command(name='warnlist')
async def warnlist_command(ctx, member: discord.Member):
    guild_id = ctx.guild.id
    member_id = member.id
    if guild_id in warnings and member_id in warnings[guild_id]:
        current_warnings = warnings[guild_id][member_id]
        await ctx.send(f"{member.mention} has {current_warnings} warning(s).")
    else:
        await ctx.send(f"{member.mention} has no warnings.")

@bot.command(name='cat')
async def cat_command(ctx):
    cat_images = ["https://placekitten.com/400/300", "https://placekitten.com/500/500"]
    await ctx.send(random.choice(cat_images))

@bot.command(name='dog')
async def dog_command(ctx):
    dog_images = ["https://placedog.net/400/300", "https://placedog.net/500/500"]
    await ctx.send(random.choice(dog_images))

@bot.command(name='coinflip')
async def coinflip_command(ctx):
    outcome = random.choice(["Heads", "Tails"])
    await ctx.send(f"🪙 The coin landed on **{outcome}**.")

@bot.command(name='rps')
async def rps_command(ctx, choice: str):
    valid_choices = ["rock", "paper", "scissors"]
    if choice.lower() not in valid_choices:
        await ctx.send("Invalid choice! Choose rock, paper, or scissors.")
        return

    bot_choice = random.choice(valid_choices)
    if choice.lower() == bot_choice:
        result = "It's a tie!"
    elif (choice.lower() == "rock" and bot_choice == "scissors") or \
         (choice.lower() == "scissors" and bot_choice == "paper") or \
         (choice.lower() == "paper" and bot_choice == "rock"):
        result = "You win!"
    else:
        result = "You lose!"

    await ctx.send(f"You chose **{choice}**, I chose **{bot_choice}**. {result}")

@bot.command(name='remind')
async def remind_command(ctx, time_in_seconds: int, *, reminder: str):
    await ctx.send(f"⏰ Reminder set for {time_in_seconds} seconds.")
    await asyncio.sleep(time_in_seconds)
    await ctx.send(f"🔔 Reminder: {reminder}")

@bot.command(name='trivia')
async def trivia_command(ctx):
    questions = [
        ("What is the capital of France?", "Paris"),
        ("How many continents are there?", "7"),
        ("Who directed the movie **Jaws**?", "Steven Spielberg"),
        ("Which desert is the largest in the world?", "Sahara Desert"),
        ("Which country has the most islands?", "Sweden"),
        ("**Troll** Question : Who's in Paris? (The answer is NOT fellas.)'", "fellas")
        ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
        ("Which planet is known as the Red Planet?", "Mars"),
        ("What is the largest ocean on Earth?", "Pacific Ocean"),
        ("Who wrote 'Pride and Prejudice'?", "Jane Austen"),
        ("What is the smallest prime number?", "2"),
        ("Who discovered penicillin?", "Alexander Fleming"),
        ("What is the chemical symbol for gold?", "Au"),
        ("Which element has the atomic number 1?", "Hydrogen"),
        ("What is the largest mammal?", "Blue whale"),
        ("Who is known as the father of modern physics?", "Albert Einstein"),
        ("What is the longest river in the world?", "Nile"),
        ("Who was the first president of the United States?", "George Washington"),
        ("What is the powerhouse of the cell?", "Mitochondria"),
        ("What is the capital city of Japan?", "Tokyo"),
        ("Who painted 'The Starry Night'?", "Vincent van Gogh"),
        ("Which Shakespeare play features the character of Prospero?", "The Tempest"),
        ("What is the square root of 64?", "8")
        ("What is the largest planet in our solar system?", "Jupiter"),
        ("Who painted the Mona Lisa?", "Leonardo da Vinci"),
        ("What year did the Titanic sink?", "1912"),
        ("What is the hardest natural substance on Earth?", "Diamond"),
        ("How many continents are there?", "7"),
        ("What is the smallest country in the world?", "Vatican City"),
        ("What is the longest river in the world?", "Nile River"),
        ("Who was the first president of the United States?", "George Washington"),
        ("Which city is known as the City of Light?", "Paris"),
        ("Which movie features a shark named Jaws?", "Jaws"),
        ("What is the main ingredient in guacamole?", "Avocado"),
        ("What is the chemical symbol for gold?", "Au"),
        ("Which ocean is the largest?", "Pacific Ocean"),
        ("How many states are in the United States?", "50"),
        ("What is the largest mammal?", "Blue whale"),
        ("Who invented the telephone?", "Alexander Graham Bell"),
        ("Which bird is known for its colorful feathers and ability to mimic human speech?", "Parrot"),
        ("What is the smallest bone in the human body?", "Stapes"),
        ("Which planet is known as the Red Planet?", "Mars"),
        ("What year did World War II end?", "1945"),
        ("What is the most common gas in Earth's atmosphere?", "Nitrogen"),
        ("Who wrote the play Romeo and Juliet?", "William Shakespeare"),
        ("Which fruit is known to keep doctors away if eaten once a day?", "Apple"),
        ("What is the capital of Italy?", "Rome"),
        ("Which country is known as the Land of the Rising Sun?", "Japan"),
        ("What is the capital of the United Kingdom?", "London"),
        ("Which animal is known as the King of the Jungle?", "Lion"),
        ("What is the currency of Japan?", "Yen"),
        ("Which movie character says 'There's no place like home'?", "Dorothy from The Wizard of Oz"),
        ("What is the largest desert in the world?", "Sahara Desert"),
        ("Who invented the lightbulb?", "Thomas Edison"),
        ("What is the square root of 64?", "8"),
        ("Which country hosted the 2016 Summer Olympics?", "Brazil"),
        ("What is the capital of Australia?", "Canberra"),
        ("Which bird is known for its long migration from North America to Central America?", "Monarch butterfly"),
        ("What is the longest running TV show?", "The Simpsons"),
        ("Who was the first man on the moon?", "Neil Armstrong"),
        ("What is the name of the fictional land in The Chronicles of Narnia?", "Narnia"),
        ("Which animal is the largest land mammal?", "Elephant"),
        ("What is the tallest mountain in the world?", "Mount Everest"),
        ("Who is the author of the Harry Potter book series?", "J.K. Rowling"),
        ("Which country is home to the Great Barrier Reef?", "Australia"),
        ("How many bones are in the human body?", "206"),
        ("What is the national sport of Canada?", "Ice hockey"),
        ("What color is the 'Exclamation Point' used in the game Super Mario?", "Yellow"),
        ("What planet is closest to the sun?", "Mercury"),
        ("Which continent is the Sahara Desert located in?", "Africa"),
        ("What is the largest country by land area?", "Russia"),
        ("Which famous scientist developed the theory of general relativity?", "Albert Einstein"),
        ("Who painted the ceiling of the Sistine Chapel?", "Michelangelo"),
        ("What is the smallest planet in our solar system?", "Mercury"),
        ("Which month has 28 days?", "All months"),
        ("Who was the first woman to fly solo across the Atlantic Ocean?", "Amelia Earhart"),
        ("Which ocean lies on the west coast of the United States?", "Pacific Ocean"),
        ("What is the world's fastest land animal?", "Cheetah"),
        ("Which company created the iPhone?", "Apple"),
        ("What is the chemical symbol for oxygen?", "O"),
        ("Which element has the atomic number 1?", "Hydrogen"),
        ("Which superhero is known as the 'Dark Knight'?", "Batman"),
        ("Which state is known as the Sunshine State?", "Florida"),
        ("Which famous wizarding school does Harry Potter attend?", "Hogwarts"),
        ("Which animal is known for its black and white fur and eating bamboo?", "Panda"),
        ("What is the tallest building in the world?", "Burj Khalifa"),
        ("Which city is the capital of Canada?", "Ottawa"),
        ("What is the name of the fairy in Peter Pan?", "Tinkerbell"),
        ("What is the largest island in the world?", "Greenland"),
        ("What element does 'O' stand for on the periodic table?", "Oxygen"),
        ("What is the capital of Spain?", "Madrid"),
        ("What is the smallest country in Africa?", "Seychelles"),
        ("Which fruit is known for having its seeds on the outside?", "Strawberry"),
        ("What was the first video game character to get his own feature film?", "Mario"),
        ("What is the most popular soft drink in the world?", "Coca-Cola"),
        ("Which is the most spoken language in the world?", "Mandarin Chinese"),
        ("Which famous landmark was a gift from France to the United States?", "Statue of Liberty"),
        ("Which country is famous for the Eiffel Tower?", "France"),
        ("Which superhero is also known as 'The Man of Steel'?", "Superman"),
        ("What is the main ingredient in sushi?", "Rice"),
        ("Which American president is featured on the $5 bill?", "Abraham Lincoln"),
        ("What color is the M on McDonald's sign?", "Red"),
        ("Who was the first woman to win a Nobel Prize?", "Marie Curie"),
        ("What is the largest continent?", "Asia"),
        ("What is the second most spoken language in the world?", "Spanish"),
        ("Which planet is known for its beautiful rings?", "Saturn"),
        ("What animal is the symbol of the World Wildlife Fund?", "Panda"),
        ("What shape has four equal sides and four right angles?", "Square"),
        ("Which superhero is known as the 'Friendly Neighborhood Spider-Man'?", "Spider-Man"),
        ("What fruit is famous for keeping the doctor away?", "Apple"),
        ("What is the hardest natural material on Earth?", "Diamond"),
        ("What color is the Great Wall of China?", "Red"),
        ("Which continent is home to the Amazon Rainforest?", "South America"),
        ("What is the largest species of shark?", "Whale Shark"),
        ("What is the tallest animal in the world?", "Giraffe"),
        ("Which country invented the pizza?", "Italy"),
        ("Which superhero can climb walls and shoot webs?", "Spider-Man")
    ]
    question, answer = random.choice(questions)
    await ctx.send(f"❓ {question}")
    
    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author

    try:
        user_response = await bot.wait_for('message', timeout=15.0, check=check)
        if user_response.content.lower() == answer.lower():
            await ctx.send("✅ Correct!")
        else:
            await ctx.send(f"❌ Incorrect. The correct answer was **{answer}**.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏳ Time's up! The correct answer was **{answer}**.")

@bot.command(name='mathquiz')
async def mathquiz_command(ctx):
    num1 = random.randint(1, 100)
    num2 = random.randint(1, 100)
    answer = num1 + num2
    await ctx.send(f"🧮 What is {num1} + {num2}?")
    
    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author

    try:
        user_response = await bot.wait_for('message', timeout=15.0, check=check)
        if int(user_response.content) == answer:
            await ctx.send("✅ Correct!")
        else:
            await ctx.send(f"❌ Incorrect. The correct answer was **{answer}**.")
    except (ValueError, asyncio.TimeoutError):
        await ctx.send(f"⏳ Time's up! The correct answer was **{answer}**.")

@bot.command(name='guessnumber')
async def guessnumber_command(ctx):
    number = random.randint(1, 10)
    await ctx.send("🎲 I'm thinking of a number between 1 and 10. Can you guess it?")
    
    def check(m):
        return m.channel == ctx.channel and m.author == ctx.author and m.content.isdigit()

    try:
        while True:
            guess = await bot.wait_for('message', check=check)
            if int(guess.content) == number:
                await ctx.send("✅ You guessed it right!")
                break
            elif int(guess.content) > number:
                await ctx.send("Too high! Try again.")
            else:
                await ctx.send("Too low! Try again.")
    except asyncio.TimeoutError:
        await ctx.send(f"⏳ Time's up! The number was **{number}**.")


@bot.command(name='joke')
async def joke_command(ctx):
    jokes = ["Why don't scientists trust atoms? Because they make up everything!",
             "What do you call fake spaghetti? An impasta!",
             "Why did the scarecrow win an award? Because he was outstanding in his field!"]
    await ctx.send(random.choice(jokes))

@bot.command(name='quote')
async def quote_command(ctx):
    quotes = ["The only limit to our realization of tomorrow is our doubts of today. – Franklin D. Roosevelt",
              "Do not watch the clock. Do what it does. Keep going. – Sam Levenson",
              "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt"]
    await ctx.send(random.choice(quotes))

@bot.command(name='8ball')
async def eightball_command(ctx, *, question: str):
    responses = ["Yes, definitely!", "No, not in a million years.", "Ask again later.", "It is certain.", "My sources say no."]
    await ctx.send(f"🎱 Question: {question}\nAnswer: {random.choice(responses)}")

@bot.command(name='announce')
@commands.has_permissions(manage_messages=True)
async def announce_command(ctx, channel: discord.TextChannel, *, message: str):
    await channel.send(f"📢 Announcement: {message}")

@bot.command(name='poll')
async def poll_command(ctx, *, question: str):
    message = await ctx.send(f"📊 **Poll**: {question}")
    await message.add_reaction("👍")
    await message.add_reaction("👎")

bot.remove_command('help')

@bot.command(name="help")
async def help_command(ctx):
    pages = [
        discord.Embed(
            title="Help - Page 1",
            description="Here's a list of all available commands and features:\n🔹 **Prefix**: `,`\n\n"
                        "**Moderation Commands**\n"
        "- `,kick <member> [reason]` - Kicks a member from the server.\n"
        "- `,ban <member> [reason]` - Bans a member from the server.\n"
        "- `,unban <member#discriminator>` - Unbans a member from the server.\n"
        "- `,timeout <member> <duration> [unit]` - Temporarily mutes a member.\n"
        "- `,untimeout <member>` - Removes the timeout from a member.\n"
        "- `,warn <member> [reason]` - Warns a member. After 3 warnings, the member is banned.\n"
        "- `,mute <member>` - Mutes a member.\n"
        "- `,unmute <member>` - Unmutes a member.\n"
        "- `,lock` - Locks the current channel.\n"
        "- `,unlock` - Unlocks the current channel.\n"
        "- `,purge <amount>` - Deletes a specified number of messages.\n"
        "- `,slowmode <seconds>` - Sets slowmode for the current channel.\n"
        "- `,clearwarns <member>` - Clears warnings for a member.\n"
        "- `,warnlist <member>` - Shows the number of warnings a member has.\n"
        "- `,softban <member> [reason]` - Temporarily bans and unbans a user to clear their messages.\n"
        "- `,banlist` - Displays the list of currently banned users.\n"
        "- `,shadowmute <member>` - Mutes a user silently.\n"
        "- `,masskick <role>` - Kicks all members of a specified role.\n"
        "- `,roleban <role>` - Bans all members of a specific role.\n"
        "- `,resetnick <member>` - Resets a user's nickname.\n"
        "- `,clearreactions <message_id>` - Clears all reactions on a message.\n"
        "- `,addrole <member> <role>` - Assigns a role to a member.\n"
        "- `,removerole <member> <role>` - Removes a role from a member.\n"
        "- `,massrole <role>` - Assigns a role to all members.\n"
        "- `,lockall` - Locks all channels in the server.\n"
        "- `,unlockall` - Unlocks all channels in the server.\n"
        "- `,mutelist` - Lists all currently muted members.\n"
        "- `,voicemute <member>` - Mutes a user in a voice channel.\n"
        "- `,voiceunmute <member>` - Unmutes a user in a voice channel.\n"
        "- `,temprole <member> <role> <duration>` - Temporarily assigns a role to a member.\n"
        "- `,tempban <member> <duration>` - Temporarily bans a user.\n"
        "- `,tempmute <member> <duration>` - Temporarily mutes a user.\n"
        "- `,forceverify <member>` - Manually verifies a user.\n"
        "- `,setautonick <role> <nickname>` - Automatically assigns nicknames to users with a specific role.\n"
        "- `,setautorole <role>` - Automatically assigns a role to new members.\n"
        "- `,massdm <role> <message>` - Sends a DM to all members of a specific role.\n"
        "- `,raidmode` - Enables raid mode, restricting new members from joining.\n"
        "- `,warnsettings` - Configures warning thresholds and actions.\n",
            color=discord.Color.blurple()
        ),
        discord.Embed(
            title="Help - Page 2",
            description="**Utility Commands**\n"
                        "- `,setjoin <channel_id>` - Sets the channel for welcome and leave messages.\n"
                        "- `,setup` - Checks if the bot has the necessary permissions.\n"
                        "- `,say <message>` - Makes the bot send a message.\n"
                        "- `,userinfo <member>` - Displays information about a member.\n"
                        "- `,serverinfo` - Displays information about the server.\n"
                        "- `,avatar <member>` - Shows a user's avatar.\n"
        "- `,roleinfo <role>` - Displays information about a role.\n"
        "- `,ping` - Shows the bot's latency.\n"
        "- `,botinfo` - Provides information about the bot.\n"
        "- `,remind <seconds> <message>` - Sets a reminder.\n"
        "- `,uptime` - Shows how long the bot has been running.\n"
        "- `,weather <city>` - Shows the current weather for a city.\n"
        "- `,urban <term>` - Searches for a term in Urban Dictionary.\n"
        "- `,checkbot` - Tests all bot commands and permissions, providing a live update.\n"
        "- `,timer <seconds>` - Sets a countdown timer.\n"
        "- `,poll <question>` - Creates a poll.\n"
        "- `,timezone <city>` - Shows the current time for a city.\n"
        "- `,calculate <expression>` - Calculates a mathematical expression.\n"
        "- `,report <member> <reason>` - Reports a member to the server's moderators.\n",
        
            color=discord.Color.blurple()
        ),
        discord.Embed(
            title="Help - Page 3",
            description="**Fun Commands**\n"
        "- `,joke` - Sends a random joke.\n"
        "- `,quote` - Sends a random inspirational quote.\n"
        "- `,8ball <question>` - Magic 8-ball response.\n"
        "- `,cat` - Sends a random cat image.\n"
        "- `,dog` - Sends a random dog image.\n"
        "- `,meme` - Sends a random meme.\n"
        "- `,coinflip` - Flips a coin.\n"
        "- `,rps <choice>` - Play rock-paper-scissors with the bot.\n"
        "- `,trivia` - Asks a random trivia question.\n"
        "- `,mathquiz` - Asks a random math question.\n"
        "- `,guessnumber` - Play a guessing game.\n"
        "- `,roll <sides>` - Rolls a dice with a specified number of sides (default 6).\n"
        "- `,motivate` - Sends a motivational quote.\n"
        "- `,countdown <seconds>` - Starts a countdown timer.\n"
        "- `,compliment <member>` - Sends a compliment to a member.\n"
        "- `,roast` - Sends a random roast.\n"
        "- `,truthordare` - Sends a truth or dare prompt.\n"
        "- `,insult <member>` - Sends a light-hearted, funny insult.\n"
        "- `,advice` - Sends random life advice.\n"
        "- `,dadjoke` - Sends a dad joke.\n"
        "- `,fact` - Sends a random fact.\n",
            color=discord.Color.blurple()
        )
    ]

    class HelpView(View):
        def __init__(self, ctx):
            super().__init__(timeout=180)
            self.ctx = ctx
            self.current_page = 0

        async def send(self):
            for child in self.children:
                if isinstance(child, Button):
                    child.disabled = (
                        (child.label == "Previous" and self.current_page == 0) or
                        (child.label == "Next" and self.current_page == len(pages) - 1)
                    )
            await ctx.send(embed=pages[self.current_page], view=self)

        @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
        async def previous_page(self, interaction: discord.Interaction, button: Button):
            self.current_page -= 1
            await interaction.response.edit_message(embed=pages[self.current_page], view=self)

        @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
        async def next_page(self, interaction: discord.Interaction, button: Button):
            self.current_page += 1
            await interaction.response.edit_message(embed=pages[self.current_page], view=self)

        @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
        async def close(self, interaction: discord.Interaction, button: Button):
            await interaction.message.delete()

    view = HelpView(ctx)
    await view.send()

@bot.command(name='warn')
@commands.has_permissions(manage_messages=True)
async def warn_command(ctx, member: discord.Member, *, reason: str = 'No reason provided'):
    guild_id = ctx.guild.id
    member_id = member.id

    if guild_id not in warnings:
        warnings[guild_id] = {}
    if member_id not in warnings[guild_id]:
        warnings[guild_id][member_id] = 0

    warnings[guild_id][member_id] += 1
    current_warnings = warnings[guild_id][member_id]

    await ctx.send(f"{member.mention} has been warned. Reason: {reason}. They now have {current_warnings} warning(s).")

    if current_warnings >= 3:
        try:
            await member.send(
                f"You have been banned from **{ctx.guild.name}** due to accumulating 3 warnings.\n"
                f"Reason for the last warning: {reason}"
            )
        except discord.Forbidden:
            print(f"Could not send DM to {member.name}")

        await member.ban(reason=f"Accumulated 3 warnings. Last reason: {reason}")
        await ctx.send(f"{member.mention} has been banned for accumulating 3 warnings.")
        warnings[guild_id][member_id] = 0

@bot.tree.command(name='meme', description='Sends a funny Meme or GIF!')
async def meme_command(ctx):
    memes = ["https://tenor.com/view/beomkyuta-cachorro-rindo-dog-laughing-gif-20922220", "https://tenor.com/view/cattwerk-gif-19230769", "https://cdn.discordapp.com/attachments/1214974799470792724/1289677388527173643/noFilter.webp", "https://cdn.discordapp.com/attachments/1280666965282656356/1286881586285117561/hawk2uhh.gif", "https://cdn.discordapp.com/attachments/1210731286390378596/1264857287336394842/lookatthisfuckingidiot.gif", "https://cdn.discordapp.com/attachments/1191914607279878320/1261717873236246540/attachment.gif", "https://tenor.com/view/milly-silly-cat-silly-silly-milly-happy-cat-gif-13373795408567336440"]
    await ctx.send(random.choice(memes))
    
@bot.command(name='meme')
async def meme_command(ctx):
    memes = ["https://tenor.com/view/beomkyuta-cachorro-rindo-dog-laughing-gif-20922220", "https://tenor.com/view/cattwerk-gif-19230769", "https://cdn.discordapp.com/attachments/1214974799470792724/1289677388527173643/noFilter.webp", "https://cdn.discordapp.com/attachments/1280666965282656356/1286881586285117561/hawk2uhh.gif", "https://cdn.discordapp.com/attachments/1210731286390378596/1264857287336394842/lookatthisfuckingidiot.gif", "https://cdn.discordapp.com/attachments/1191914607279878320/1261717873236246540/attachment.gif", "https://tenor.com/view/milly-silly-cat-silly-silly-milly-happy-cat-gif-13373795408567336440"]
    await ctx.send(random.choice(memes))

@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick_command(ctx, member: discord.Member, *, reason: str = 'No reason provided'):
    await member.kick(reason=reason)
    await ctx.send(f'{member.mention} has been kicked. Reason: {reason}')

@bot.tree.command(name='kick', description='Kicks a member from the server')
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = 'No reason provided'):
    await member.kick(reason=reason)
    await interaction.response.send_message(f'{member.mention} has been kicked. Reason: {reason}', ephemeral=True)

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban_command(ctx, member: discord.Member, *, reason: str = 'No reason provided'):
    try:
        await member.send(
            f"You were banned from **{ctx.guild.name}**.\n"
            f"Reason: {reason}"
        )
    except discord.Forbidden:
        print(f"Could not send DM to {member.name}")

    await member.ban(reason=reason)
    await ctx.send(f'{member.mention} has been banned. Reason: {reason}')

@bot.command(name='unban')
@commands.has_permissions(ban_members=True)
async def unban_command(ctx, *, member_name: str):
    banned_users = []
    async for ban_entry in ctx.guild.bans():
        banned_users.append(ban_entry)

    member_name, member_discriminator = member_name.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} has been unbanned.')
            return

    await ctx.send(f'User {member_name}#{member_discriminator} not found in the ban list.')

@bot.tree.command(name='unban', description='Unbans a user from the server')
@app_commands.checks.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, member_name: str):
    banned_users = []
    async for ban_entry in interaction.guild.bans():
        banned_users.append(ban_entry)

    member_name, member_discriminator = member_name.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await interaction.guild.unban(user)
            await interaction.response.send_message(f'{user.mention} has been unbanned.', ephemeral=True)
            return

    await interaction.response.send_message(f'User {member_name}#{member_discriminator} not found in the ban list.', ephemeral=True)

@bot.command(name='timeout')
@commands.has_permissions(moderate_members=True)
async def timeout_command(ctx, member: discord.Member, duration: int, unit: str = 'm'):
    time_units = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days'}
    if unit not in time_units:
        await ctx.send("Invalid time unit! Use 's' for seconds, 'm' for minutes, 'h' for hours, or 'd' for days.")
        return

    delta_args = {time_units[unit]: duration}
    try:
        timeout_until = discord.utils.utcnow() + timedelta(**delta_args)
        await member.edit(timed_out_until=timeout_until)
        await ctx.send(f'{member.mention} has been timed out for {duration} {unit}.')
    except discord.Forbidden:
        await ctx.send("I do not have permission to timeout this member.")
    except discord.HTTPException:
        await ctx.send("Failed to timeout the member.")

@bot.command(name='untimeout')
@commands.has_permissions(moderate_members=True)
async def untimeout_command(ctx, member: discord.Member):
    try:
        await member.edit(timed_out_until=None)
        await ctx.send(f'{member.mention} has been un-timed out.')
    except discord.Forbidden:
        await ctx.send("I do not have permission to remove the timeout from this member.")
    except discord.HTTPException:
        await ctx.send("Failed to remove the timeout from the member.")

@bot.tree.command(name='timeout', description='Times out a member for a specified duration')
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, duration: int, unit: str = 'm'):
    time_units = {'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days'}
    if unit not in time_units:
        await interaction.response.send_message("Invalid time unit! Use 's' for seconds, 'm' for minutes, 'h' for hours, or 'd' for days.", ephemeral=True)
        return

    delta_args = {time_units[unit]: duration}
    try:
        timeout_until = discord.utils.utcnow() + timedelta(**delta_args)
        await member.edit(timed_out_until=timeout_until)
        await interaction.response.send_message(f'{member.mention} has been timed out for {duration} {unit}.', ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to timeout this member.", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("Failed to timeout the member.", ephemeral=True)

@bot.tree.command(name='untimeout', description='Removes the timeout from a member')
@app_commands.checks.has_permissions(moderate_members=True)
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.edit(timed_out_until=None)
        await interaction.response.send_message(f'{member.mention} has been un-timed out.', ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("I do not have permission to remove the timeout from this member.", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("Failed to remove the timeout from the member.", ephemeral=True)
        
        
# --- Fact Command ---
@bot.command(name='fact')
async def fact_command(ctx):
    facts = [
        "Honey never spoils.",
        "Bananas are berries, but strawberries aren't.",
        "A day on Venus is longer than a year on Venus."
    ]
    await ctx.send(random.choice(facts))

# --- Server Status Command ---
@bot.command(name='serverstatus')
async def server_status_command(ctx):
    embed = discord.Embed(
        title="Server Status",
        description=f"Server Name: {ctx.guild.name}\nTotal Members: {ctx.guild.member_count}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

# --- Anti-Swearing Feature ---
bad_words = ['badword1', 'badword2', 'badword3']

@bot.event
async def on_message(message):
    if any(word in message.content.lower() for word in bad_words):
        await message.delete()
        await message.channel.send(f"{message.author.mention}, please refrain from using inappropriate language.")
    await bot.process_commands(message)

# --- Dad Joke Command ---
@bot.command(name='dadjoke')
async def dadjoke_command(ctx):
    jokes = [
        "I'm reading a book on anti-gravity. It's impossible to put down!",
        "Why did the math book look sad? Because it had too many problems.",
        "What do you call cheese that isn't yours? Nacho cheese."
    ]
    await ctx.send(random.choice(jokes))

# --- Blackjack Command ---
@bot.command(name='blackjack')
async def blackjack_command(ctx):
    def draw_card():
        return random.randint(1, 11)

    player_cards = [draw_card(), draw_card()]
    dealer_cards = [draw_card(), draw_card()]

    await ctx.send(f"Your cards: {player_cards} (Total: {sum(player_cards)})\nDealer's visible card: {dealer_cards[0]}")

    while sum(player_cards) < 21:
        await ctx.send("Type 'hit' to draw another card or 'stand' to hold.")
        try:
            msg = await bot.wait_for('message', timeout=30.0, check=lambda m: m.author == ctx.author)
            if msg.content.lower() == 'hit':
                player_cards.append(draw_card())
                await ctx.send(f"Your cards: {player_cards} (Total: {sum(player_cards)})")
            elif msg.content.lower() == 'stand':
                break
            else:
                await ctx.send("Invalid input.")
        except asyncio.TimeoutError:
            await ctx.send("Game timed out.")
            return

    player_total = sum(player_cards)
    dealer_total = sum(dealer_cards)

    await ctx.send(f"Dealer's cards: {dealer_cards} (Total: {dealer_total})")

    if player_total > 21:
        await ctx.send("You busted! Dealer wins.")
    elif dealer_total > 21 or player_total > dealer_total:
        await ctx.send("You win!")
    elif player_total == dealer_total:
        await ctx.send("It's a tie!")
    else:
        await ctx.send("Dealer wins!")

@bot.command(name='report')
async def report_command(ctx, member: discord.Member, *, reason: str):
    report_channel = discord.utils.get(ctx.guild.channels, name='reports')
    if report_channel:
        embed = discord.Embed(
            title="New Report",
            description=f"Reporter: {ctx.author.mention}\nReported: {member.mention}\nReason: {reason}",
            color=discord.Color.red()
        )
        await report_channel.send(embed=embed)
        await ctx.send("Your report has been submitted.")
    else:
        await ctx.send("Report channel not found. Please create a channel named 'reports'.")

@bot.command(name='hangman')
async def hangman_command(ctx):
    words = ['python', 'discord', 'hangman', 'development']
    word = random.choice(words)
    guessed = ['_'] * len(word)
    attempts = 6
    await ctx.send(' '.join(guessed))

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and len(m.content) == 1

    while attempts > 0 and '_' in guessed:
        try:
            guess_msg = await bot.wait_for('message', timeout=30.0, check=check)
            guess = guess_msg.content.lower()
            if guess in word:
                for idx, letter in enumerate(word):
                    if letter == guess:
                        guessed[idx] = guess
                await ctx.send('Correct! ' + ' '.join(guessed))
            else:
                attempts -= 1
                await ctx.send(f"Incorrect! Attempts remaining: {attempts}")
        except asyncio.TimeoutError:
            await ctx.send("Game timed out.")
            return

    if '_' not in guessed:
        await ctx.send("Congratulations, you've guessed the word!")
    else:
        await ctx.send(f"You've run out of attempts. The word was **{word}**.")

@bot.command(name='riddle')
async def riddle_command(ctx):
    riddles = [
        {"question": "What has keys but can't open locks?", "answer": "Keyboard"},
        {"question": "What runs around the yard without moving?", "answer": "Fence"}
    ]
    riddle = random.choice(riddles)
    await ctx.send(riddle['question'])

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        answer_msg = await bot.wait_for('message', timeout=30.0, check=check)
        if answer_msg.content.lower() == riddle['answer'].lower():
            await ctx.send("Correct!")
        else:
            await ctx.send(f"Incorrect. The answer was **{riddle['answer']}**.")
    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The answer was **{riddle['answer']}**.")

@bot.command(name='memorygame')
async def memory_game_command(ctx):
    numbers = [random.randint(1, 99) for _ in range(5)]
    memory_message = await ctx.send(f"Remember these numbers: {' '.join(map(str, numbers))}")
    await asyncio.sleep(5)
    await memory_message.delete()
    await ctx.send("Now, type the numbers you remember in order.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        response = await bot.wait_for('message', timeout=30.0, check=check)
        user_numbers = list(map(int, response.content.split()))
        if user_numbers == numbers:
            await ctx.send("Good job! You got it, you have good memory! (Unless your using Vencord :rage:)")
        else:
            await ctx.send(f"Oops, try again. The correct sequence was: {' '.join(map(str, numbers))}")
    except asyncio.TimeoutError:
        await ctx.send(f"Time's up! The sequence was: {' '.join(map(str, numbers))}")

@bot.command(name='tictactoe')
async def tictactoe_command(ctx, opponent: discord.Member):
    if opponent == ctx.author:
        await ctx.send("You can't play against yourself!")
        return

    board = [' ' for _ in range(9)]
    current_player = ctx.author

    def print_board():
        return (
            f"{board[0]}|{board[1]}|{board[2]}\n"
            f"-+-+-\n"
            f"{board[3]}|{board[4]}|{board[5]}\n"
            f"-+-+-\n"
            f"{board[6]}|{board[7]}|{board[8]}"
        )

    await ctx.send(f"Tic Tac Toe game between {ctx.author.mention} and {opponent.mention}\n" + print_board())

    def check(m):
        return m.author == current_player and m.channel == ctx.channel and m.content.isdigit()

    for _ in range(9):
        await ctx.send(f"{current_player.mention}, choose a position (1-9):")
        try:
            move = await bot.wait_for('message', timeout=30.0, check=check)
            pos = int(move.content) - 1
            if board[pos] == ' ':
                board[pos] = 'X' if current_player == ctx.author else 'O'
                await ctx.send(print_board())
                # Check for win conditions here (omitted for brevity)
                current_player = opponent if current_player == ctx.author else ctx.author
            else:
                await ctx.send("Position already taken.")
        except asyncio.TimeoutError:
            await ctx.send(f"{current_player.mention} took too long to respond.")
            return
    await ctx.send("Game over!")

@bot.command(name='truthordare')
async def truth_or_dare_command(ctx):
    await ctx.send("Type 'truth' or 'dare'.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', timeout=15.0, check=check)
        if msg.content.lower() == 'truth':
            truths = [
                "What is your deepest fear?",
                "Have you ever lied to a friend?"
            ]
            await ctx.send(random.choice(truths))
        elif msg.content.lower() == 'dare':
            dares = [
                "Sing the chorus of your favorite song.",
                "Do 10 push-ups."
            ]
            await ctx.send(random.choice(dares))
        else:
            await ctx.send("Invalid choice.")
    except asyncio.TimeoutError:
        await ctx.send("Time's up!")

@bot.command(name='wiki')
async def wiki_command(ctx, *, query: str):
    try:
        summary = wikipedia.summary(query, sentences=2)
        await ctx.send(f"**{query.capitalize()}**\n{summary}")
    except wikipedia.DisambiguationError as e:
        await ctx.send(f"Disambiguation error: {e}")
    except wikipedia.exceptions.PageError:
        await ctx.send("Page not found.")

@bot.command(name='insult')
async def insult_command(ctx, member: discord.Member = None):
    member = member or ctx.author
    insults = [
        "You're as bright as a black hole, and twice as dense.",
        "I would agree with you, but then we'd both be wrong."
    ]
    await ctx.send(f"{member.mention}, {random.choice(insults)}")

@bot.command(name='advice')
async def advice_command(ctx):
    advices = [
        "Believe in yourself.",
        "Stay positive, work hard, make it happen.",
        "Don't watch the clock; do what it does. Keep going."
    ]
    await ctx.send(random.choice(advices))

@bot.command(name='addbadword')
@commands.has_permissions(manage_messages=True)
async def add_bad_word(ctx, word: str):
    bad_words.append(word.lower())
    await ctx.send(f"Added '{word}' to the list of bad words.")
    
    # --- Softban Command ---
@bot.command(name='softban')
@commands.has_permissions(ban_members=True)
async def softban(ctx, member: discord.Member, *, reason="No reason provided"):
    await ctx.guild.ban(member, reason=reason, delete_message_days=1)
    await ctx.guild.unban(member, reason="Softban completed")
    await ctx.send(f"{member.mention} has been softbanned. Reason: {reason}")

# --- Banlist Command ---
@bot.command(name='banlist')
@commands.has_permissions(ban_members=True)
async def banlist(ctx):
    bans = await ctx.guild.bans()
    if not bans:
        await ctx.send("No users are banned in this server.")
        return
    banned_users = "\n".join([f"{ban.user} (Reason: {ban.reason})" for ban in bans])
    await ctx.send(f"**Banned Users:**\n{banned_users}")

# --- Shadowmute Command ---
@bot.command(name='shadowmute')
@commands.has_permissions(manage_roles=True)
async def shadowmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)
    await member.add_roles(muted_role)
    await ctx.send(f"{member.mention} has been shadowmuted.")

# --- Masskick Command ---
@bot.command(name='masskick')
@commands.has_permissions(kick_members=True)
async def masskick(ctx, role: discord.Role):
    members_to_kick = [member for member in role.members]
    for member in members_to_kick:
        await member.kick(reason="Masskick initiated")
    await ctx.send(f"Kicked {len(members_to_kick)} members with the role {role.name}.")

# --- Roleban Command ---
@bot.command(name='roleban')
@commands.has_permissions(ban_members=True)
async def roleban(ctx, role: discord.Role):
    members_to_ban = [member for member in role.members]
    for member in members_to_ban:
        await ctx.guild.ban(member, reason="Role-based ban")
    await ctx.send(f"Banned {len(members_to_ban)} members with the role {role.name}.")

# --- Reset Nickname Command ---
@bot.command(name='resetnick')
@commands.has_permissions(manage_nicknames=True)
async def resetnick(ctx, member: discord.Member):
    await member.edit(nick=None)
    await ctx.send(f"Reset nickname for {member.mention}.")

# --- Clear Reactions Command ---
@bot.command(name='clearreactions')
@commands.has_permissions(manage_messages=True)
async def clearreactions(ctx, message_id: int):
    try:
        message = await ctx.channel.fetch_message(message_id)
        await message.clear_reactions()
        await ctx.send("Cleared all reactions from the message.")
    except discord.NotFound:
        await ctx.send("Message not found.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to clear reactions.")

# --- Add Role Command ---
@bot.command(name='addrole')
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"Added role {role.name} to {member.mention}.")

# --- Remove Role Command ---
@bot.command(name='removerole')
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"Removed role {role.name} from {member.mention}.")

# --- Lock All Channels Command ---
@bot.command(name='lockall')
@commands.has_permissions(manage_channels=True)
async def lockall(ctx):
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Locked all channels.")

# --- Unlock All Channels Command ---
@bot.command(name='unlockall')
@commands.has_permissions(manage_channels=True)
async def unlockall(ctx):
    for channel in ctx.guild.channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Unlocked all channels.")

# --- Mute List Command ---
@bot.command(name='mutelist')
async def mutelist(ctx):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role:
        muted_members = [member.mention for member in muted_role.members]
        await ctx.send(f"Muted Members: {', '.join(muted_members)}")
    else:
        await ctx.send("No muted members found.")

# --- Force Verify Command ---
@bot.command(name='forceverify')
@commands.has_permissions(manage_roles=True)
async def forceverify(ctx, member: discord.Member):
    verified_role = discord.utils.get(ctx.guild.roles, name="Verified")
    if not verified_role:
        verified_role = await ctx.guild.create_role(name="Verified")
    await member.add_roles(verified_role)
    await ctx.send(f"{member.mention} has been force-verified.")

# --- Tempban Command ---
@bot.command(name='tempban')
@commands.has_permissions(ban_members=True)
async def tempban(ctx, member: discord.Member, duration: int, *, reason="No reason provided"):
    await ctx.guild.ban(member, reason=reason)
    await ctx.send(f"{member.mention} has been banned for {duration} seconds. Reason: {reason}")

    await asyncio.sleep(duration)
    await ctx.guild.unban(member)
    await ctx.send(f"{member.mention} has been unbanned after the temporary ban duration.")

# --- Raid Mode Command ---
@bot.command(name='raidmode')
@commands.has_permissions(administrator=True)
async def raidmode(ctx, enable: bool = True):
    if enable:
        await ctx.guild.edit(verification_level=discord.VerificationLevel.high)
        await ctx.send("Raid mode enabled: Only users with verified email addresses can join.")
    else:
        await ctx.guild.edit(verification_level=discord.VerificationLevel.low)
        await ctx.send("Raid mode disabled.")

# Function to check if an account is suspicious
def is_suspicious_account(member: discord.Member):
    account_age = (datetime.datetime.utcnow() - member.created_at).days
    return account_age < SUSPICIOUS_ACCOUNT_AGE_DAYS

# Function to create and send the verification panel
async def send_verification_panel(channel: discord.TextChannel, role_to_give: discord.Role, role_to_remove: discord.Role):
    embed = discord.Embed(
        title="Verification Required",
        description="Click the button below to verify and gain access to the server.",
        color=discord.Color.green()
    )

    button = discord.ui.Button(label="Verify", style=discord.ButtonStyle.green)

    async def button_callback(interaction: discord.Interaction):
        member = interaction.user
        if is_suspicious_account(member):
            await interaction.response.send_message(
                "Your account appears suspicious (recently created). Please contact an admin.",
                ephemeral=True
            )
            return

        if role_to_give:
            await member.add_roles(role_to_give)

        if role_to_remove:
            await member.remove_roles(role_to_remove)

        await interaction.response.send_message(
            "You have been successfully verified!", ephemeral=True
        )

    button.callback = button_callback
    view = discord.ui.View()
    view.add_item(button)

    await channel.send(embed=embed, view=view)

# Prefix command
@bot.command()
@commands.has_permissions(administrator=True)
async def send_verification(ctx, channel: discord.TextChannel, role_to_give: discord.Role, role_to_remove: discord.Role):
    await send_verification_panel(channel, role_to_give, role_to_remove)
    await ctx.send(f"Verification panel sent to {channel.mention} with role {role_to_give.mention} assigned and {role_to_remove.mention} removed!")

# Slash command
@bot.tree.command(name="send_verification", description="Send a verification panel to a channel.")
@app_commands.describe(
    channel="The channel where the verification panel will be sent.",
    role_to_give="The role to give when verified.",
    role_to_remove="The role to remove when verified."
)
@app_commands.default_permissions(administrator=True)
async def send_verification_slash(interaction: discord.Interaction, channel: discord.TextChannel, role_to_give: discord.Role, role_to_remove: discord.Role):
    await send_verification_panel(channel, role_to_give, role_to_remove)
    await interaction.response.send_message(
        f"Verification panel sent to {channel.mention} with role {role_to_give.mention} assigned and {role_to_remove.mention} removed!",
        ephemeral=True
    )        
    
@bot.command(name='joinvc')
async def join_vc(ctx):
    """Joins the voice channel of the command user."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
            await ctx.send(f"Joined {channel.name}!")
        else:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"Moved to {channel.name}!")
    else:
        await ctx.send("You need to be in a voice channel for me to join!")

@bot.command(name='leavevc')
async def leave_vc(ctx):
    """Leaves the current voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel!")
    else:
        await ctx.send("I'm not connected to any voice channel.")

# Roles for verification
unverified_role_id = None
verified_role_id = None

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.gray, custom_id="verify_button", emoji="<:verify:1353140527943516221>")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        if unverified_role_id is None or verified_role_id is None:
            await interaction.response.send_message(
                "Verification roles have not been set up. Please contact an admin.", ephemeral=True
            )
            return

        member = interaction.user
        unverified_role = interaction.guild.get_role(unverified_role_id)
        verified_role = interaction.guild.get_role(verified_role_id)

        if unverified_role in member.roles:
            await member.remove_roles(unverified_role)
            await member.add_roles(verified_role)
            await interaction.response.send_message("You have been verified! Enjoy your free boosts!", ephemeral=True)
        else:
            await interaction.response.send_message("You are already verified.", ephemeral=True)

@bot.hybrid_command(name="setup_verify", description="Set up verification roles for boosts", with_app_command=False)
@commands.has_permissions(administrator=True)
async def setup_verify(ctx, unverified: discord.Role, verified: discord.Role):
    global unverified_role_id, verified_role_id
    unverified_role_id = unverified.id
    verified_role_id = verified.id
    await ctx.message.delete()
    await ctx.send(f"Verification roles set up.\nUnverified: {unverified.name}\nVerified: {verified.name}", ephemeral = True)

@bot.hybrid_command(name="send_verify_panel", description="Send the cool verification panel")
@commands.has_permissions(administrator=True)
async def send_verify_panel(ctx):
    embed = discord.Embed(
        title="Server Boosts Verification",
        description=(
            "🔓 **Verify to access your free boosts!**\n\n"
            "📧 **Requirements:** Email verification\n"
            "🌎 **Locations:** US, UK, Canada (No VPN required)\n"
            "⛏️ **Difficulty:** Easy\n\n"
            "Subscribe to receive emails from our partners and claim your free server boosts! :kulid_boostanim:\n"
            "The more emails you read, the more boosts you get.\n\n"
            "**Claim INFINITE Server Boosts**\n"
            "Simple and easy to complete as always 💖"
        ),
        color=discord.Color.from_rgb(41, 45, 46) # Gray embed color
    )
    embed.set_footer(text="Press 'Verify' to complete the process!")
    await ctx.send(embed=embed, view=VerifyView())

@bot.hybrid_command(name="dm", description="Send a direct message to another user")
async def dm(ctx, user: discord.User, *, message: str):
    try:
        await user.send(f"Message from {ctx.author}: {message}")
        await ctx.send("Message sent successfully.", ephemeral=True)
    except discord.Forbidden:
        await ctx.send("I couldn't send a message to that user. They might have DMs disabled.", ephemeral=True)

@bot.hybrid_command(name="echo", description="Repeat a message")
async def echo(ctx, *, message: str):
    await ctx.send(message)

@bot.hybrid_command(name="avatar", description="Show a user's avatar")
async def avatar(ctx, user: discord.User = None):
    user = user or ctx.author
    embed = discord.Embed(title=f"{user.name}'s Avatar", color=discord.Color.blue())
    embed.set_image(url=user.avatar.url)
    await ctx.send(embed=embed)

    # Slash command for creating the boost panel (admin only)
@bot.tree.command(name="boost-panel", description="Creates a boost panel in the current channel")
@app_commands.default_permissions(administrator=True)
async def boost_panel(interaction: discord.Interaction):
    # Create the embed for the boost panel
    boost_embed = discord.Embed(
        title="🚀 Claim Your Free Discord Boost! 🚀",
        description="Support our server by claiming your free boost! Click the button below to get started.",
        color=0xFF73FA  # Discord Nitro pink color
    )
    
    # Add fields to the embed
    boost_embed.add_field(
        name="✨ Benefits",
        value="Boost our server to unlock exclusive perks and help us grow!",
        inline=False
    )
    boost_embed.add_field(
        name="⏱️ Limited Time", 
        value="This offer is available for a limited time only. Claim yours now!",
        inline=False
    )
    boost_embed.set_footer(text="Thanks for supporting our community!")
    
    # Create the button for the panel
    claim_button = discord.ui.Button(
        style=discord.ButtonStyle.primary,
        label="Claim Free Boost",
        emoji="🚀",
        custom_id="claim_boost"
    )
    
    # Create view and add button
    view = discord.ui.View()
    view.add_item(claim_button)
    
    # Send the embed with button
    await interaction.response.send_message(embed=boost_embed, view=view)

# Button interaction handler
@bot.event
async def on_interaction(interaction: discord.Interaction):
    # Check if it's a button interaction with the correct custom_id
    if interaction.type == discord.InteractionType.component:
        if interaction.data.get("custom_id") == "claim_boost":
            try:
                # Create the DM embed
                dm_embed = discord.Embed(
                    title="🚀 Boost Our Server!",
                    description="Please click the button below to boost your server",
                    color=0xFF73FA
                )
                dm_embed.set_image(url="https://i.imgur.com/XYZ123.png")  # Replace with your own image
                dm_embed.set_footer(text="Thank you for your support!")
                
                # Create boost button for DM
                boost_button = discord.ui.Button(
                    style=discord.ButtonStyle.link,
                    label="Boost Now",
                    url="https://agape-boosts.vercel.app"
                )
                
                # Create view and add button
                dm_view = discord.ui.View()
                dm_view.add_item(boost_button)
                
                # Send DM to the user
                await interaction.user.send(embed=dm_embed, view=dm_view)
                
                # Acknowledge the interaction with ephemeral message
                await interaction.response.send_message(
                    content="Check your DMs to claim your free server boost!",
                    ephemeral=True
                )
            except Exception as e:
                logging.error(f"Error sending DM: {e}")
                await interaction.response.send_message(
                    content="I couldn't send you a DM. Please make sure your DMs are open and try again.",
                    ephemeral=True
                )
                
    
# --- MASS BAN ---
@bot.tree.command(name="massban", description="Ban multiple users at once by user IDs (comma separated).")
@app_commands.checks.has_permissions(ban_members=True)
async def massban_slash(interaction: discord.Interaction, user_ids: str, reason: str = "No reason provided"):
    ids = [uid.strip() for uid in user_ids.split(",")]
    banned = []
    failed = []
    for uid in ids:
        try:
            user = await interaction.guild.fetch_member(int(uid))
            await interaction.guild.ban(user, reason=reason)
            banned.append(str(user))
        except Exception:
            failed.append(uid)
    await interaction.response.send_message(
        f"Banned: {', '.join(banned)}\nFailed: {', '.join(failed)}"
    )

@bot.command(name="massban")
@commands.has_permissions(ban_members=True)
async def massban_command(ctx, user_ids: str, *, reason: str = "No reason provided"):
    ids = [uid.strip() for uid in user_ids.split(",")]
    banned = []
    failed = []
    for uid in ids:
        try:
            user = await ctx.guild.fetch_member(int(uid))
            await ctx.guild.ban(user, reason=reason)
            banned.append(str(user))
        except Exception:
            failed.append(uid)
    await ctx.send(f"Banned: {', '.join(banned)}\nFailed: {', '.join(failed)}")

# --- MASS MUTE (Timeout) ---
@bot.tree.command(name="massmute", description="Timeout multiple users at once by user IDs (comma separated).")
@app_commands.checks.has_permissions(moderate_members=True)
async def massmute_slash(interaction: discord.Interaction, user_ids: str, minutes: int = 10, reason: str = "No reason provided"):
    ids = [uid.strip() for uid in user_ids.split(",")]
    muted = []
    failed = []
    until = discord.utils.utcnow() + timedelta(minutes=minutes)
    for uid in ids:
        try:
            member = await interaction.guild.fetch_member(int(uid))
            await member.timeout(until, reason=reason)
            muted.append(str(member))
        except Exception:
            failed.append(uid)
    await interaction.response.send_message(
        f"Muted: {', '.join(muted)}\nFailed: {', '.join(failed)}"
    )

@bot.command(name="massmute")
@commands.has_permissions(moderate_members=True)
async def massmute_command(ctx, user_ids: str, minutes: int = 10, *, reason: str = "No reason provided"):
    ids = [uid.strip() for uid in user_ids.split(",")]
    muted = []
    failed = []
    until = discord.utils.utcnow() + timedelta(minutes=minutes)
    for uid in ids:
        try:
            member = await ctx.guild.fetch_member(int(uid))
            await member.timeout(until, reason=reason)
            muted.append(str(member))
        except Exception:
            failed.append(uid)
    await ctx.send(f"Muted: {', '.join(muted)}\nFailed: {', '.join(failed)}")

# --- MASS UNMUTE (Remove Timeout) ---
@bot.tree.command(name="massunmute", description="Remove timeout from multiple users by user IDs (comma separated).")
@app_commands.checks.has_permissions(moderate_members=True)
async def massunmute_slash(interaction: discord.Interaction, user_ids: str):
    ids = [uid.strip() for uid in user_ids.split(",")]
    unmuted = []
    failed = []
    for uid in ids:
        try:
            member = await interaction.guild.fetch_member(int(uid))
            await member.timeout(None)
            unmuted.append(str(member))
        except Exception:
            failed.append(uid)
    await interaction.response.send_message(
        f"Unmuted: {', '.join(unmuted)}\nFailed: {', '.join(failed)}"
    )

@bot.command(name="massunmute")
@commands.has_permissions(moderate_members=True)
async def massunmute_command(ctx, user_ids: str):
    ids = [uid.strip() for uid in user_ids.split(",")]
    unmuted = []
    failed = []
    for uid in ids:
        try:
            member = await ctx.guild.fetch_member(int(uid))
            await member.timeout(None)
            unmuted.append(str(member))
        except Exception:
            failed.append(uid)
    await ctx.send(f"Unmuted: {', '.join(unmuted)}\nFailed: {', '.join(failed)}")

# --- MASS WARN (Simple warning system) ---
@bot.tree.command(name="masswarn", description="Warn multiple users at once by user IDs (comma separated).")
@app_commands.checks.has_permissions(moderate_members=True)
async def masswarn_slash(interaction: discord.Interaction, user_ids: str, reason: str = "No reason provided"):
    ids = [uid.strip() for uid in user_ids.split(",")]
    warned = []
    failed = []
    for uid in ids:
        try:
            member = await interaction.guild.fetch_member(int(uid))
            warnings.setdefault(member.id, []).append(reason)
            warned.append(str(member))
        except Exception:
            failed.append(uid)
    await interaction.response.send_message(
        f"Warned: {', '.join(warned)}\nFailed: {', '.join(failed)}"
    )

@bot.command(name="masswarn")
@commands.has_permissions(moderate_members=True)
async def masswarn_command(ctx, user_ids: str, *, reason: str = "No reason provided"):
    ids = [uid.strip() for uid in user_ids.split(",")]
    warned = []
    failed = []
    for uid in ids:
        try:
            member = await ctx.guild.fetch_member(int(uid))
            warnings.setdefault(member.id, []).append(reason)
            warned.append(str(member))
        except Exception:
            failed.append(uid)
    await ctx.send(f"Warned: {', '.join(warned)}\nFailed: {', '.join(failed)}")

# --- AUDIT LOG (Show last 5 moderation actions) ---
@bot.tree.command(name="audit", description="Show recent moderation actions.")
@app_commands.checks.has_permissions(view_audit_log=True)
async def audit_slash(interaction: discord.Interaction):
    entries = []
    async for entry in interaction.guild.audit_logs(limit=5):
        entries.append(f"{entry.action} - {entry.user} -> {entry.target}")
    await interaction.response.send_message("\n".join(entries) or "No recent moderation actions.")

@bot.command(name="audit")
@commands.has_permissions(view_audit_log=True)
async def audit_command(ctx):
    entries = []
    async for entry in ctx.guild.audit_logs(limit=5):
        entries.append(f"{entry.action} - {entry.user} -> {entry.target}")
    await ctx.send("\n".join(entries) or "No recent moderation actions.")

# --- ANTI-INVITE (Delete messages with Discord invite links) ---
anti_invite_enabled = {}

@bot.tree.command(name="antiinvite", description="Toggle anti-invite protection on or off.")
@app_commands.checks.has_permissions(manage_messages=True)
async def antiinvite_slash(interaction: discord.Interaction, state: str):
    anti_invite_enabled[interaction.guild.id] = state.lower() == "on"
    await interaction.response.send_message(f"Anti-invite set to {state}.")

@bot.command(name="antiinvite")
@commands.has_permissions(manage_messages=True)
async def antiinvite_command(ctx, state: str):
    anti_invite_enabled[ctx.guild.id] = state.lower() == "on"
    await ctx.send(f"Anti-invite set to {state}.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    # Anti-invite
    if anti_invite_enabled.get(message.guild.id, False):
        if "discord.gg/" in message.content or "discord.com/invite/" in message.content:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, invite links are not allowed.")
            return
    await bot.process_commands(message)

# --- MASS WARNINGS SYSTEM (view, clear) ---
@bot.tree.command(name="modnotes", description="Show all moderation notes for a user.")
@app_commands.checks.has_permissions(moderate_members=True)
async def modnotes_slash(interaction: discord.Interaction, member: discord.Member):
    notes = warnings.get(member.id, [])
    await interaction.response.send_message(f"Warnings for {member.mention}: {notes or 'No warnings.'}")

@bot.command(name="modnotes")
@commands.has_permissions(moderate_members=True)
async def modnotes_command(ctx, member: discord.Member):
    notes = warnings.get(member.id, [])
    await ctx.send(f"Warnings for {member.mention}: {notes or 'No warnings.'}")

# --- SET SLOWMODE ---
@bot.tree.command(name="setslowmode", description="Set slowmode for the current channel.")
@app_commands.checks.has_permissions(manage_channels=True)
async def setslowmode_slash(interaction: discord.Interaction, seconds: int):
    await interaction.channel.edit(slowmode_delay=seconds)
    await interaction.response.send_message(f"Set slowmode to {seconds} seconds.")

@bot.command(name="setslowmode")
@commands.has_permissions(manage_channels=True)
async def setslowmode_command(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"Set slowmode to {seconds} seconds.")

@bot.tree.command(name="removeslowmode", description="Remove slowmode from the current channel.")
@app_commands.checks.has_permissions(manage_channels=True)
async def removeslowmode_slash(interaction: discord.Interaction):
    await interaction.channel.edit(slowmode_delay=0)
    await interaction.response.send_message("Removed slowmode.")

@bot.command(name="removeslowmode")
@commands.has_permissions(manage_channels=True)
async def removeslowmode_command(ctx):
    await ctx.channel.edit(slowmode_delay=0)
    await ctx.send("Removed slowmode.")

# --- NICKNAME MANAGEMENT ---
@bot.tree.command(name="nickname", description="Change a user's nickname.")
@app_commands.checks.has_permissions(manage_nicknames=True)
async def nickname_slash(interaction: discord.Interaction, member: discord.Member, nickname: str):
    await member.edit(nick=nickname)
    await interaction.response.send_message(f"Changed nickname for {member.mention} to {nickname}.")

@bot.command(name="nickname")
@commands.has_permissions(manage_nicknames=True)
async def nickname_command(ctx, member: discord.Member, nickname: str):
    await member.edit(nick=nickname)
    await ctx.send(f"Changed nickname for {member.mention} to {nickname}.")

# --- MODMAIL (Send message to mods) ---
@bot.tree.command(name="modmail", description="Send a message to the moderators (sends to admins).")
async def modmail_slash(interaction: discord.Interaction, message: str):
    mod_role = discord.utils.get(interaction.guild.roles, permissions=discord.Permissions(administrator=True))
    if mod_role:
        for member in mod_role.members:
            try:
                await member.send(f"Modmail from {interaction.user}: {message}")
            except Exception:
                continue
        await interaction.response.send_message("Modmail sent.")
    else:
        await interaction.response.send_message("No admin/mod role found.")

@bot.command(name="modmail")
async def modmail_command(ctx, *, message: str):
    mod_role = discord.utils.get(ctx.guild.roles, permissions=discord.Permissions(administrator=True))
    if mod_role:
        for member in mod_role.members:
            try:
                await member.send(f"Modmail from {ctx.author}: {message}")
            except Exception:
                continue
        await ctx.send("Modmail sent.")
    else:
        await ctx.send("No admin/mod role found.")

# --- MODLOG (Show last 10 moderation actions) ---
@bot.tree.command(name="modlog", description="Show the moderation log for the server.")
@app_commands.checks.has_permissions(view_audit_log=True)
async def modlog_slash(interaction: discord.Interaction):
    entries = []
    async for entry in interaction.guild.audit_logs(limit=10):
        entries.append(f"{entry.action} - {entry.user} -> {entry.target}")
    await interaction.response.send_message("\n".join(entries) or "No moderation actions found.")

@bot.command(name="modlog")
@commands.has_permissions(view_audit_log=True)
async def modlog_command(ctx):
    entries = []
    async for entry in ctx.guild.audit_logs(limit=10):
        entries.append(f"{entry.action} - {entry.user} -> {entry.target}")
    await ctx.send("\n".join(entries) or "No moderation actions found.")

# --- MODPING (Ping all moderators) ---
@bot.tree.command(name="modping", description="Ping all moderators (role with ban_members).")
@app_commands.checks.has_permissions(mention_everyone=True)
async def modping_slash(interaction: discord.Interaction):
    mod_role = discord.utils.get(interaction.guild.roles, permissions=discord.Permissions(ban_members=True))
    if mod_role:
        await interaction.response.send_message(f"{mod_role.mention} Attention needed!")
    else:
        await interaction.response.send_message("No moderator role found.")

@bot.command(name="modping")
@commands.has_permissions(mention_everyone=True)
async def modping_command(ctx):
    mod_role = discord.utils.get(ctx.guild.roles, permissions=discord.Permissions(ban_members=True))
    if mod_role:
        await ctx.send(f"{mod_role.mention} Attention needed!")
    else:
        await ctx.send("No moderator role found.")

# --- APPEAL (Send appeal to mods) ---
@bot.tree.command(name="appeal", description="Submit an appeal for a moderation action (sends to admins).")
async def appeal_slash(interaction: discord.Interaction, case_id: int, message: str):
    mod_role = discord.utils.get(interaction.guild.roles, permissions=discord.Permissions(administrator=True))
    if mod_role:
        for member in mod_role.members:
            try:
                await member.send(f"Appeal from {interaction.user} (Case {case_id}): {message}")
            except Exception:
                continue
        await interaction.response.send_message("Appeal sent.")
    else:
        await interaction.response.send_message("No admin/mod role found.")

@bot.command(name="appeal")
async def appeal_command(ctx, case_id: int, *, message: str):
    mod_role = discord.utils.get(ctx.guild.roles, permissions=discord.Permissions(administrator=True))
    if mod_role:
        for member in mod_role.members:
            try:
                await member.send(f"Appeal from {ctx.author} (Case {case_id}): {message}")
            except Exception:
                continue
        await ctx.send("Appeal sent.")
    else:
        await ctx.send("No admin/mod role found.")

# --- Add more commands as needed using this structure ---





async def missing_permissions_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)

bot.tree.error(missing_permissions_error)

keep_alive()
bot.run(os.environ["DISCORD_BOT_TOKEN"])
