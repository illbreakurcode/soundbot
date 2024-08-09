import os
os.system("pip3 install -r requirements.txt")
import subprocess
import json
import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import asyncio
import threading
from werkzeug.security import generate_password_hash, check_password_hash
from getpass import getpass

if not os.path.exists("./sounds"):
    os.makedirs("sounds")

CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    "sound_files": {},
    "guild_id": "",
    "channel_id": "",
    "discord_token": "YOUR_DISCORD_TOKEN",
    "flask": {
        "host": "127.0.0.1",
        "port": 5000,
        "username": "admin",
        "password": generate_password_hash("password123")
    }
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

if(not os.path.exists(CONFIG_FILE)):
    guildid = int(input('Enter Guild ID: '))
    channelid = int(input('Enter Channel ID: '))
    token = input('Enter Bot Token: ')
    ipv4 = input('Bind IPv4? (Default: 0.0.0.0): ')  or '0.0.0.0'
    port = int(input('Enter Port (Default: 5000): ') or 5000)
    user = input('Enter Username (Default: admin): ') or 'admin'
    pw = getpass('Enter Password: ')
    DEFAULT_CONFIG = {
    "sound_files": {},
    "guild_id": f"{guildid}",
    "channel_id": f"{channelid}",
    "discord_token": f"{token}", 
    "flask": {
        "host": f"{ipv4}",
        "port": port,
        "username": f"{user}",
        "password": generate_password_hash(pw),
        "password": pw
        }
    }
    save_config(DEFAULT_CONFIG)
    print()
    print("Pleas run following command and configure your password (note: you have to be in the bots root directory): ")
    print(f"$ cd public && htpasswd -c .htpasswd {user}")
    exit(0)

def add_sounds_from_directory():
    sounds_directory = 'sounds'
    config = load_config()
    
    for filename in os.listdir(sounds_directory):
        if filename.endswith('.mp3'):
            sound_name = os.path.splitext(filename)[0]
            sound_path = os.path.join(sounds_directory, filename)
            
            if filename not in str(config["sound_files"]):
                config["sound_files"][sound_name] = sound_path

    save_config(config)

config = load_config()

# Discord-Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.dm_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Flask App Setup
app = Flask(__name__, static_folder='public')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/sounds', methods=['GET'])
def get_sounds():
    return jsonify(config["sound_files"])

@app.route('/api/sounds/add', methods=['POST'])
def add_sound():
    data = request.json
    name = data.get('name')
    path = data.get('path')
    if name and path:
        config["sound_files"][name] = path
        save_config(config)
        return jsonify({"message": "Sound added."})
    return jsonify({"message": "Invalid input."}), 400

@app.route('/api/sounds/remove', methods=['POST'])
def remove_sound():
    data = request.json
    name = data.get('name')
    if name in config["sound_files"]:
        del config["sound_files"][name]
        save_config(config)
        return jsonify({"message": "Sound removed."})
    return jsonify({"message": "Sound not found."}), 404

@app.route('/api/sounds/rename', methods=['POST'])
def rename_sound():
    data = request.json
    old_name = data.get('oldName')
    new_name = data.get('newName')
    if old_name in config["sound_files"] and new_name not in config["sound_files"]:
        config["sound_files"][new_name] = config["sound_files"].pop(old_name)
        save_config(config)
        return jsonify({"message": "Sound renamed."})
    return jsonify({"message": "Invalid input or name already exists."}), 400

@app.route('/api/sounds/play', methods=['POST'])
def play_sound():
    data = request.json
    name = data.get('name')
    if name in config["sound_files"]:
        guild_id = config["guild_id"]
        asyncio.run_coroutine_threadsafe(play_sound_coroutine(guild_id, name), bot.loop)
        return jsonify({"message": "Playing sound."})
    return jsonify({"message": "Sound not found."}), 404

async def play_sound_coroutine(guild_id, sound_name):
    guild = bot.get_guild(int(guild_id))
    if guild and guild.voice_client:
        source = discord.FFmpegPCMAudio(config["sound_files"][sound_name])
        guild.voice_client.play(source)

@app.route('/api/channel/join', methods=['POST'])
def join_channel_api():
    data = request.json
    guild_id = data.get('guild_id', config["guild_id"])
    channel_id = data.get('channel_id', config["channel_id"])
    asyncio.run_coroutine_threadsafe(join_channel_coroutine(guild_id, channel_id), bot.loop)
    return jsonify({"message": "Joining channel."})

async def join_channel_coroutine(guild_id, channel_id):
    guild = bot.get_guild(int(guild_id))
    if guild:
        channel = guild.get_channel(int(channel_id))
        if channel:
            if not guild.voice_client:
                try:
                    await channel.connect()
                    print(f"Successfully joined channel {channel_id}")
                except Exception as e:
                    print(f"Failed to join channel: {e}")
            else:
                print("Bot is already connected to a voice channel.")
        else:
            print(f"Channel with ID {channel_id} not found.")
    else:
        print(f"Guild with ID {guild_id} not found.")

@app.route('/api/channel/leave', methods=['POST'])
def leave_channel_api():
    data = request.json
    guild_id = data.get('guild_id', config["guild_id"])
    asyncio.run_coroutine_threadsafe(leave_channel_coroutine(guild_id), bot.loop)
    return jsonify({"message": "Leaving channel."})

async def leave_channel_coroutine(guild_id):
    guild = bot.get_guild(int(guild_id))
    if guild and guild.voice_client:
        await guild.voice_client.disconnect()
        print(f"Disconnected from channel in guild {guild_id}")
    else:
        print(f"No active voice client in guild {guild_id}")

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    if guild_id and channel_id:
        config["guild_id"] = guild_id
        config["channel_id"] = channel_id
        save_config(config)
        return jsonify({"message": "Settings updated."})
    return jsonify({"message": "Invalid input."}), 400

@app.route('/api/settings', methods=['GET'])
def get_settings():
    return jsonify({
        "guild_id": config["guild_id"],
        "channel_id": config["channel_id"]
    })

@app.route('/api/sounds/stop', methods=['POST'])
def stop_sound():
    guild_id = config["guild_id"]
    asyncio.run_coroutine_threadsafe(stop_sound_coroutine(guild_id), bot.loop)
    return jsonify({"message": "Stopping sound."})

async def stop_sound_coroutine(guild_id):
    guild = bot.get_guild(int(guild_id))
    if guild and guild.voice_client:
        guild.voice_client.stop()
        print(f"Stopped sound in channel for guild {guild_id}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    add_sounds_from_directory()

@bot.command(name='play')
async def play(ctx, sound_name: str):
    guild_id = ctx.guild.id
    await play_sound_coroutine(guild_id, sound_name)

@bot.command(name='stop')
async def stop(ctx):
    guild_id = ctx.guild.id
    await stop_sound_coroutine(guild_id)

@bot.command(name='join')
async def join(ctx, channel_id: str):
    channel_id = channel_id.strip('<>#')
    if channel_id == '1262035383718383630':
        guild_id = ctx.guild.id
        await join_channel_coroutine(guild_id, channel_id)
    else:
        await ctx.send("Invalid channel ID format or channel ID does not match the known ID.")

@bot.command(name='leave')
async def leave(ctx):
    guild_id = ctx.guild.id
    await leave_channel_coroutine(guild_id)

@bot.command(name='list')
async def list(ctx):
    sound_names = config["sound_files"].keys()
    embed = discord.Embed(title="Available Sounds", color=discord.Color.blue())
    
    embed.description = "\n".join(sound_names)
    
    await ctx.send(embed=embed)

def run_flask_app():
    app.run(host=config["flask"]["host"], port=config["flask"]["port"])

if __name__ == '__main__':
    watchdog_process = subprocess.Popen(['python3', 'watchdog_script.py'])
    
    try:
        threading.Thread(target=run_flask_app).start()
        bot.run(config["discord_token"])
    finally:
        watchdog_process.terminate()
