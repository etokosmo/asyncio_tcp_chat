import asyncio
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class InvalidToken(Exception):
    pass


@asynccontextmanager
async def open_connection(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    try:
        yield reader, writer
    except InvalidToken:
        pass
    finally:
        logger.info('Close the connection')
        writer.close()
        await writer.wait_closed()
