# Description: Add your page endpoints here.

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from .crud import get_owner_data_by_id

clnrest_generic_router = APIRouter()


def clnrest_renderer():
    return template_renderer(["clnrest/templates"])


#######################################
##### ADD YOUR PAGE ENDPOINTS HERE ####
#######################################


# Backend admin page


@clnrest_generic_router.get("/", response_class=HTMLResponse)
async def index(req: Request, user: User = Depends(check_user_exists)):
    return clnrest_renderer().TemplateResponse(
        "clnrest/index.html", {"request": req, "user": user.json()}
    )


# Frontend shareable page


@clnrest_generic_router.get("/{owner_data_id}")
async def owner_data_public_page(req: Request, owner_data_id: str):
    owner_data = await get_owner_data_by_id(owner_data_id)
    if not owner_data:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Owner Data does not exist.")

    public_page_name = getattr(owner_data, "", "")
    public_page_description = getattr(owner_data, "", "")

    return clnrest_renderer().TemplateResponse(
        "clnrest/public_page.html",
        {
            "request": req,
            "owner_data_id": owner_data_id,
            "public_page_name": public_page_name,
            "public_page_description": public_page_description,
        },
    )


