from fastapi import APIRouter
from lnbits.db import Database

from .views import clnrest_generic_router
from .views_api import clnrest_api_router

db = Database("ext_clnrest")
clnrest_ext: APIRouter = APIRouter(prefix="/clnrest", tags=["CLNREST"])
clnrest_ext.include_router(clnrest_generic_router)
clnrest_ext.include_router(clnrest_api_router)


clnrest_static_files = [
    {
        "path": "/clnrest/static",
        "name": "clnrest_static",
    }
]

__all__ = [
    "clnrest_ext",
    "clnrest_static_files",
]
