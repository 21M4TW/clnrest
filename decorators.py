from fastapi import Request, Security
from fastapi.security.api_key import APIKeyHeader
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import require_admin_key, require_invoice_key

api_key_header_auth = APIKeyHeader(
    name="rune",
    auto_error=True,
    description="Admin or Invoice key for CLNREST API's",
)


async def clnrest_require_admin_key(request: Request, api_key_header_auth: str = Security(api_key_header_auth)):
    return await require_admin_key(request, api_key_header_auth)


async def clnrest_require_invoice_key(
    request: Request, api_key_header_auth: str = Security(api_key_header_auth)
) -> WalletTypeInfo:
    return await require_invoice_key(request, api_key_header_auth)
