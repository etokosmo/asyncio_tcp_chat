import asyncio
import datetime

import aiofiles


async def save_message(message):
    current_time = datetime.datetime.now()
    message = f"{current_time.strftime('[%d.%m.%y %H:%M]')} {message}"
    print(message)
    async with aiofiles.open('chat_history', mode='a') as chat_file:
        await chat_file.write(message)


async def tcp_reader():
    reader, writer = await asyncio.open_connection(
        'minechat.dvmn.org', 5000)

    while not reader.at_eof():
        message = await reader.readline()
        await save_message(message.decode())

    print('Close the connection')
    writer.close()


asyncio.run(tcp_reader())
