import asyncio
import logging
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


@asynccontextmanager
async def open_connection(host, port):
    conn = await asyncio.open_connection(host, port)
    reader, writer = conn
    try:
        yield conn
    finally:
        logger.info('Close the connection')
        writer.close()
        await writer.wait_closed()
