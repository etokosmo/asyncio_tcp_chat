import argparse
import asyncio
import datetime
import logging

import aiofiles
from environs import Env

logger = logging.getLogger(__name__)


async def save_message(message, chat_history_filename):
    current_time = datetime.datetime.now()
    message = f"{current_time.strftime('[%d.%m.%y %H:%M]')} {message}"
    logger.info(message)
    async with aiofiles.open(chat_history_filename, mode='a') as chat_file:
        await chat_file.write(message)


async def tcp_reader(tcp_config):
    reader, writer = await asyncio.open_connection(
        tcp_config['host'], tcp_config['port'])

    while not reader.at_eof():
        message = await reader.readline()
        await save_message(message.decode(), tcp_config['history'])

    logger.info('Close the connection')
    writer.close()


if __name__ == '__main__':
    logging.basicConfig(
        filename='logs.log',
        format='%(levelname)s:%(name)s:%(message)s',
        level=logging.INFO
    )
    logging.getLogger().addHandler(logging.StreamHandler())

    tcp_config = {}
    env = Env()
    env.read_env()
    tcp_config['host'] = env.str('HOST', 'minechat.dvmn.org')
    tcp_config['port'] = env.int('PORT', 5000)
    tcp_config['history'] = env.str('HISTORY', 'chat_history.txt')
    parser = argparse.ArgumentParser(description='Communicate with TCP chat')
    parser.add_argument('--host', help='host of chat')
    parser.add_argument('--port', type=int, help='port of chat')
    parser.add_argument('--history', help='path to file with chat history')
    args = parser.parse_args()
    for key, value in vars(args).items():
        tcp_config[key] = value or tcp_config[key]
    asyncio.run(tcp_reader(tcp_config))
