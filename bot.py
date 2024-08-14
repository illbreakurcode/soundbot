import os
os.system("pip3 install -r requirements.txt")
import subprocess
import json
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask, request, jsonify, render_template
import asyncio
import threading
import myinstants_api
from werkzeug.security import generate_password_hash, check_password_hash
from getpass import getpass
import requests
from urllib.parse import unquote

if not os.path.exists("./sounds"):
    os.makedirs("sounds")

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

if not os.path.exists(CONFIG_FILE):
    guildid = int(input('Enter Guild ID: '))
    channelid = int(input('Enter Channel ID: '))
    token = input('Enter Bot Token: ')
    sounds_dir = input('How should the folder with the sounds in it be called? ')
    ipv4 = input('Bind IPv4? (Default: 0.0.0.0): ')  or '0.0.0.0'
    port = int(input('Enter Port (Default: 5000): ') or 5000)
    user = input('Enter Username (Default: admin): ') or 'admin'
    pw = getpass('Enter Password: ')
    CUSTOM_CONFIG = {
        "sound_files": {},
        "sounds_dir": f"{sounds_dir}",
        "guild_id": f"{guildid}",
        "channel_id": f"{channelid}",
        "discord_token": f"{token}",
        "flask": {
            "host": f"{ipv4}",
            "port": port,
            "username": f"{user}",
            "password": generate_password_hash(pw),
            "password_clear": pw
        }
    }
    pw = None
    save_config(CUSTOM_CONFIG)
    print()
    print("Please run the following command and configure your password (note: you have to be in the bot's root directory): ")
    print(f"$ cd public && htpasswd -c .htpasswd {user}")
    exit(0)

def add_sounds_from_directory():
    global config
    sounds_directory = str(config["sounds_dir"])
    config = load_config()
    
    for filename in os.listdir(sounds_directory):
        if filename.endswith('.mp3'):
            sound_name = os.path.splitext(filename)[0]
            sound_path = os.path.join(sounds_directory, filename)
            
            if filename not in str(config["sound_files"]):
                config["sound_files"][sound_name] = sound_path

    sounds = config["sound_files"].items()

    keys_to_delete = [sound_name for sound_name, sound_path in sounds if not os.path.exists(sound_path)]

    for key in keys_to_delete:
        del config["sound_files"][key]

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

@app.route('/api/myinstants/search', methods=['GET'])
def search_myinstants():
    search_term = request.args.get('name', '')  # Hole den Suchbegriff aus den Query-Parametern
    return myinstants_api.search(search_term)

@app.route('/api/myinstants/play', methods=['POST'])
def play_myinstants_sound():
    data = request.json
    guild_id = data.get('guild_id')
    url = data.get('url')

    if not guild_id or not url:
        return jsonify({'error': 'Missing guild_id or url'}), 400

    voice_client = bot.get_guild(int(guild_id)).voice_client

    if voice_client and voice_client.is_connected():
        # Play the sound directly from the URL
        voice_client.play(discord.FFmpegPCMAudio(url))
        return jsonify({'status': 'playing'}), 200
    else:
        return jsonify({'error': 'Bot is not connected to a voice channel'}), 400

@app.route('/api/myinstants/download', methods=['POST'])
def download_myinstants_sound():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'Missing URL'}), 400
    
    try:
        # Extrahiere den Dateinamen aus der URL
        filename = unquote(url.split('/')[-1]) + '.mp3'
        filename = filename.replace(".mp3.mp3", ".mp3")
        filepath = os.path.join(config["sounds_dir"], filename)
        
        # Sound von MyInstants herunterladen
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
                print("downloaded")
            return jsonify({'status': 'downloaded', 'name': filename}), 200
        else:
            return jsonify({'error': 'Failed to download sound'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    add_sounds_from_directory()

    # Register all commands globally on all servers
    try:
        await bot.tree.sync()
        print("Slash commands synced globally.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# Define slash commands
@bot.tree.command(name='play')
async def play(interaction: discord.Interaction, sound_name: str):
    guild_id = interaction.guild.id
    await play_sound_coroutine(guild_id, sound_name)
    await interaction.response.send_message(f"Playing sound: {sound_name}")

@bot.tree.command(name='stop')
async def stop(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    await stop_sound_coroutine(guild_id)
    await interaction.response.send_message("Sound stopped.")

@bot.tree.command(name='join')
async def join(interaction: discord.Interaction, channel_id: str = None):
    if channel_id:
        channel_id = channel_id.strip('<>#')
        if channel_id == '1262035383718383630':
            guild_id = interaction.guild.id
            await join_channel_coroutine(guild_id, channel_id)
            await interaction.response.send_message(f"Joined channel {channel_id}.")
        else:
            await interaction.response.send_message("Invalid channel ID format or channel ID does not match the known ID.", ephemeral=True)
    else:
        if interaction.user.voice and interaction.user.voice.channel:
            channel = interaction.user.voice.channel
            await channel.connect()
            await interaction.response.send_message(f"Joined channel {channel.id}.")
        else:
            await interaction.response.send_message("You are not connected to a voice channel and no channel ID was provided.", ephemeral=True)

@bot.tree.command(name='leave')
async def leave(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    await leave_channel_coroutine(guild_id)
    await interaction.response.send_message("Left the voice channel.")

@bot.tree.command(name='list')
async def list(interaction: discord.Interaction):
    sound_names = config["sound_files"].keys()
    embed = discord.Embed(title="Available Sounds", color=discord.Color.blue())
    
    embed.description = "\n".join(sound_names)
    
    await interaction.response.send_message(embed=embed)

def run_flask_app():
    app.run(host=config["flask"]["host"], port=config["flask"]["port"])

if __name__ == '__main__':
    watchdog_process = subprocess.Popen(['python3', 'watchdog_script.py'])
    
    try:
        threading.Thread(target=run_flask_app).start()
        bot.run(config["discord_token"])
    finally:
        watchdog_process.terminate()