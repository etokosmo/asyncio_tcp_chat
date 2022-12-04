import argparse
import asyncio
import json
import logging

import aiofiles
from environs import Env

logger = logging.getLogger(__name__)


async def register(reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                   tcp_config):
    """Registration new user"""
    writer.write("\n".encode())
    await writer.drain()

    response = await reader.readline()
    logger.info(response.decode())

    username = tcp_config['username']
    if not tcp_config['username']:
        username = input('У вас отсутствует токен. Введите ваше имя: ')

    writer.write(f"{username}\n\n".encode())
    logger.info(f'SEND: {username}')

    response = await reader.readline()
    decoded_response = json.loads(response)
    logger.info(decoded_response)
    minechat_user_token = decoded_response.get('account_hash')
    async with aiofiles.open('.env', mode='a') as env_file:
        await env_file.write(f'\nMINECHAT_USER_TOKEN={minechat_user_token}')
    await writer.drain()


async def authorise(tcp_config):
    """Authorization user"""
    reader, writer = await asyncio.open_connection(
        tcp_config['host'], tcp_config['port'])

    response = await reader.readline()
    logger.info(response.decode())
    if tcp_config['token']:
        writer.write(f"{tcp_config['token']}\n".encode())
        await writer.drain()

        response = await reader.readline()
        decoded_response = json.loads(response)

        if not decoded_response:
            logger.info('Неправильный токен. Отправляем на регистрацию ...')
            writer.close()
            reader, writer = await asyncio.open_connection(
                tcp_config['host'], tcp_config['port'])
            response = await reader.readline()
            logger.info(response.decode())
            await register(reader, writer, tcp_config)
    else:
        await register(reader, writer, tcp_config)
    return reader, writer


async def tcp_writer(tcp_config):
    try:
        reader, writer = await authorise(tcp_config)
        message = tcp_config['msg']
        writer.write(f"{message}\n\n".encode())
        logger.info(f'SEND: {message}')
        await writer.drain()
    finally:
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

    asyncio.run(tcp_writer(tcp_config))
