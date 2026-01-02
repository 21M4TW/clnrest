from fastapi import APIRouter, Depends, Request
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer


def clnrest_renderer():
    return template_renderer(["clnrest/templates"])


clnrest_generic_router = APIRouter()


@clnrest_generic_router.get("/")
async def clnrest_index(request: Request, user: User = Depends(check_user_exists)):
    return clnrest_renderer().TemplateResponse("clnrest/index.html", {"request": request, "user": user.json()})
