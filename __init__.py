import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db
from .tasks import wait_for_paid_invoices
from .views import clnrest_generic_router
from .views_api import clnrest_api_router

clnrest_ext: APIRouter = APIRouter(
    prefix="/clnrest", tags=["CLNREST"]
)
clnrest_ext.include_router(clnrest_generic_router)
clnrest_ext.include_router(clnrest_api_router)


clnrest_static_files = [
    {
        "path": "/clnrest/static",
        "name": "clnrest_static",
    }
]

scheduled_tasks: list[asyncio.Task] = []


def clnrest_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def clnrest_start():
    task = create_permanent_unique_task("ext_clnrest", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = [
    "db",
    "clnrest_ext",
    "clnrest_start",
    "clnrest_static_files",
    "clnrest_stop",
]