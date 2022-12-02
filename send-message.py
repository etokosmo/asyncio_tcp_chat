import argparse
import asyncio
import json
import logging

from environs import Env

logger = logging.getLogger(__name__)


async def register(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    writer.write("\n".encode())
    await writer.drain()

    response = await reader.readline()
    logger.info(response.decode())

    username = input('У вас отсутствует токен. Введите ваше имя: ')
    writer.write(f"{username}\n\n".encode())
    logger.info(f'SEND: {username}')
    await writer.drain()


async def tcp_writer(tcp_config):
    reader, writer = await asyncio.open_connection(
        tcp_config['host'], tcp_config['port'])

    response = await reader.readline()
    logger.info(response.decode())
    if tcp_config['token']:
        writer.write(f"{tcp_config['token']}\n".encode())
        await writer.drain()
    else:
        await register(reader, writer)
    response = await reader.readline()
    decoded_response = json.loads(response)
    logger.info(response)
    if not decoded_response:
        logger.info('Неправильный токен. Отправляем на регистрацию ...')
        reader, writer = await asyncio.open_connection(
            tcp_config['host'], tcp_config['port'])
        await register(reader, writer)

    while True:
        message = input('Введите ваше сообщение: ')
        writer.write(f"{message}\n\n".encode())
        logger.info(f'SEND: {message}')
        await writer.drain()

    print('Close the connection')
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
    parser = argparse.ArgumentParser(description='Communicate with TCP chat')
    parser.add_argument('--host', help='host of chat')
    parser.add_argument('--port', type=int, help='port of chat')
    parser.add_argument('--token', type=int, help='user token')
    args = parser.parse_args()
    for key, value in vars(args).items():
        tcp_config[key] = value or tcp_config[key]
    asyncio.run(tcp_writer(tcp_config))
