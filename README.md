# Connect to secret chat

Script to connect to the secret chat

## What is possible

* Connect to chat.
* Save chat history.
* Send message.

## Scripts

* listen-message.py - to save chat history.
* send-message.py - to send message.

## Configurations

* Python version: 3.9
* Libraries: [requirements.txt](https://github.com/etokosmo/asyncio_tcp_chat/blob/main/requirements.txt)

## Launch

- Download code
- Through the console in the directory with the code, install the virtual environment with the command:
```bash
python3 -m venv env
```

- Activate the virtual environment with the command:
```bash
source env/bin/activate
```

- Install the libraries with the command:
```bash
pip install -r requirements.txt
```

- Write the environment variables in the `.env` file in the format KEY=VALUE

`HOST` - Host of Chat. Default=`minechat.dvmn.org`.

`PORT` - Port of Chat. Default=`5000` to read; `5050` to send.

`HISTORY` - Path to file to save chat history. Default=`chat_history.txt` in current directory.

`MINECHAT_USER_TOKEN` - Your chat token. If you haven't then don't fill this field.

`USERNAME` - Your username if you haven't MINECHAT_USER_TOKEN to log in.


### listen-message.py
- Start with the command:
```bash
python3 listen-message.py
```
- Optional Arguments:
```bash
--host # Host of Chat. 
--port # Port of Chat. 
--history # Path to file to save chat history. 
```

### send-message.py
- Start with the command:
```bash
python3 listen-message.py <your_message>
```
- Optional Arguments:
```bash
--host # Host of Chat. 
--port # Port of Chat. 
--token # Your chat token. 
--username # Your username if you haven't MINECHAT_USER_TOKEN to log in. 
```

> Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).