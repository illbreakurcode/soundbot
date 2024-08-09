# soundbot
This is a small discord.py soundboard bot with HTTP-API and webinterface using flask. 

I got the initial code with a Tkinther interface from https://github.com/JonasB2510
I changed it so it is using flask as an WebUI with HTTP-Basic-Auth

# Install: 
`$ git clone https://github.com/illbreakurcode/soundbot` 

`$ cd soundbot` 

`$ python3 bot.py` 

Configure the config by following the commands in the console.
<details>
  <summary>Where to get GuildID</summary>
  To get the server ID for the first parameter, open Discord, go to Settings → Advanced and enable developer mode. Then, right-click on the server title and select "Copy ID" to get the guild ID.
</details>
<details>
  <summary>Where to get ChannelID</summary>
  To get the server ID for the first parameter, open Discord, go to Settings → Advanced and enable developer mode. Then, right-click on the voice channel and select "Copy ID" to get the channel ID.
</details>
<details>
  <summary>Where to get a bot token</summary>
  To get a Bot/Bot token first go to https://discord.com/developers/applications and click on new application, type in a name read & agree the TOS & policy. Now on the side click on bot then scroll down and enable "Message Content Intent". Now go to oauth2 on the side. Now select bot > administrator (or "View Channels", "Connect", "Speak" ⚠️ Only tested with Adminitstator permissions ⚠️) now copy your url at the bottom and copy it into a new tab and add the bot to your server.
</details>
<details>
  <summary>I don't have the htpasswd command</summary>
    Install the apache2-utils packet. e.g.:
  
    `$ sudo apt install apache2-utils`
</details>

Now add sound files to the sounds directory and start the bot with `$ python3 bot.py`

# Features that maybe get added in the future:
 - being able to disable the webui
 - !list command
 - MyInstants API
 - better command support
 - being able to disable the HTTP-Basic-Auth
 - automaticly generating the .htaccess using python
 - multi user support
 - upload sound functionality (using command with download link & a `<input type=file>` on the webside)
