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

# API Documentation

## **Authentifizierung**

All API-Endpoints are password protected and require a HTTP Basic Auth header.

## API Endpoints

<details>
<summary><strong>1. Get Sounds</strong></summary>

- **Endpoint:** `/api/sounds`
- **Method:** `GET`
- **Description:** Gets a list of all registered sounds.

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    'http://127.0.0.1:5000/api/sounds',
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>

<details>
<summary><strong>2. Add Sound</strong></summary>

- **Endpoint:** `/api/sounds/add`
- **Method:** `POST`
- **Description:** Registers a soundfile.

**Body example:**

```json
{
    "name": "example_sound",
    "path": "sounds/example_sound.mp3"
}
```

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

data = {
    "name": "example_sound",
    "path": "sounds/example_sound.mp3"
}

response = requests.post(
    'http://127.0.0.1:5000/api/sounds/add',
    json=data,
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>

<details>
<summary><strong>3. Remove Sound</strong></summary>

- **Endpoint:** `/api/sounds/remove`
- **Method:** `POST`
- **Description:** Unregisters a soundfile.

**Body example:**

```json
{
    "name": "example_sound"
}
```

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

data = {
    "name": "example_sound"
}

response = requests.post(
    'http://127.0.0.1:5000/api/sounds/remove',
    json=data,
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>

<details>
<summary><strong>4. Rename Sound</strong></summary>

- **Endpoint:** `/api/sounds/rename`
- **Method:** `POST`
- **Description:** Changes the name of an registrated sound.

**Body example:**

```json
{
    "oldName": "example_sound",
    "newName": "new_example_sound"
}
```

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

data = {
    "oldName": "example_sound",
    "newName": "new_example_sound"
}

response = requests.post(
    'http://127.0.0.1:5000/api/sounds/rename',
    json=data,
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>

<details>
<summary><strong>5. Play Sound</strong></summary>

- **Endpoint:** `/api/sounds/play`
- **Method:** `POST`
- **Description:** Plays a sound.

**Body example:**

```json
{
    "name": "example_sound"
}
```

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

data = {
    "name": "example_sound"
}

response = requests.post(
    'http://127.0.0.1:5000/api/sounds/play',
    json=data,
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>

<details>
<summary><strong>6. Stop Sound</strong></summary>

- **Endpoint:** `/api/sounds/stop`
- **Method:** `POST`
- **Description:** Stops the audio.

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.post(
    'http://127.0.0.1:5000/api/sounds/stop',
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>

<details>
<summary><strong>7. Join Channel</strong></summary>

- **Endpoint:** `/api/channel/join`
- **Method:** `POST`
- **Description:** Make the bot join a specific channel.

**Body example:**

```json
{
    "guild_id": "1234567890123456789",
    "channel_id": "1234567890123456789"
}
```

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

data = {
    "guild_id": "1234567890123456789",
    "channel_id": "1234567890123456789"
}

response = requests.post(
    'http://127.0.0.1:5000/api/channel/join',
    json=data,
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>

<details>
<summary><strong>8. Leave Channel</strong></summary>

- **Endpoint:** `/api/channel/leave`
- **Method:** `POST`
- **Description:** Make the bot leave.

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.post(
    'http://127.0.0.1:5000/api/channel/leave',
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>

<details>
<summary><strong>9. Update Settings</strong></summary>

- **Endpoint:** `/api/settings`
- **Method:** `POST`
- **Description:** Changes the settings for `guild_id` and `channel_id`.

**Body example:**

```json
{
    "guild_id": "1234567890123456789",
    "channel_id": "1234567890123456789"
}
```

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

data = {
    "guild_id": "1234567890123456789",
    "channel_id": "1234567890123456789"
}

response = requests.post(
    'http://127.0.0.1:5000/api/settings',
    json=data,
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>

<details>
<summary><strong>10. Get Settings</strong></summary>

- **Endpoint:** `/api/settings`
- **Method:** `GET`
- **Description:** Gets the current setting of: (`guild_id` and `channel_id`)

**Request example:**

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    'http://127.0.0.1:5000/api/settings',
    auth=HTTPBasicAuth('admin', 'password123')
)
print(response.json())
```
</details>


# Features that maybe get added in the future:
 - being able to disable the webui
 - MyInstants API
 - better command support
 - being able to disable the HTTP-Basic-Auth
 - automaticly generating the .htaccess using python
 - multi user support
 - upload sound functionality (using command with download link & a `<input type=file>` on the webside)
