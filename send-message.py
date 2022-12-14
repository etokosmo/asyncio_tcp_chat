import argparse
import asyncio
import json
import logging

import aiofiles
from environs import Env

from tcp_tools import open_connection, MissingUsername

logger = logging.getLogger(__name__)


async def write_to_socket(writer: asyncio.StreamWriter, message: str):
    """Write the data to the underlying socket immediately"""
    writer.write(message.encode())
    await writer.drain()


async def register(reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                   username: str):
    """Registration new user"""
    await write_to_socket(writer, "\n")

    response = await reader.readline()
    logger.info(response.decode())

    await write_to_socket(writer, f"{username}\n\n")
    logger.info(f'SEND USERNAME: {username}')

    response = await reader.readline()
    decoded_response = json.loads(response)
    logger.info(decoded_response)
    minechat_user_token = decoded_response.get('account_hash')
    async with aiofiles.open('.env', mode='a') as env_file:
        await env_file.write(f'\nMINECHAT_USER_TOKEN={minechat_user_token}')


async def authorise(reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                    token: str):
    """Authorization user"""
    await write_to_socket(writer, f"{token}\n")

    response = await reader.readline()
    decoded_response = json.loads(response)
    return decoded_response


async def handle_chat(tcp_config):
    async with open_connection(tcp_config['host'], tcp_config['port']) as conn:
        reader, writer = conn
        response = await reader.readline()
        logger.info(response.decode())

        if tcp_config['token']:
            user = await authorise(reader, writer, tcp_config['token'])

            if not user:
                logger.info(
                    'Неправильный токен. Отправляем на регистрацию ...')
                username = tcp_config['username']
                if not tcp_config['username']:
                    raise MissingUsername('У вас отсутствует username')
                await register(reader, writer, username)
        else:
            username = tcp_config['username']
            if not tcp_config['username']:
                raise MissingUsername('У вас отсутствует username')
            await register(reader, writer, username)

        message = tcp_config['msg']
        await write_to_socket(writer, f"{message}\n\n")
        logger.info(f'SEND: {message}')


def main():
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
    tcp_config['port'] = env.int('PORT', 5050)
    tcp_config['token'] = env.str('MINECHAT_USER_TOKEN', None)
    tcp_config['username'] = env.str('USERNAME', None)
    tcp_config['msg'] = env.str('MESSAGE', None)

    parser = argparse.ArgumentParser(description='Communicate with TCP chat')
    parser.add_argument('msg', help='message')
    parser.add_argument('--host', help='host of chat')
    parser.add_argument('--port', type=int, help='port of chat')
    parser.add_argument('--token', help='user token')
    parser.add_argument('--username', help='username')
    args = parser.parse_args()
    for key, value in vars(args).items():
        tcp_config[key] = value or tcp_config[key]

    asyncio.run(handle_chat(tcp_config))


if __name__ == '__main__':
    main()
