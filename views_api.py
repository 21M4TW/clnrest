from http import HTTPStatus
from math import ceil

from bolt11 import decode as bolt11_decode
from fastapi import APIRouter, Depends, HTTPException
from lnbits.core.crud import get_offers, get_payments, get_standalone_offer
from lnbits.core.db import db
from lnbits.core.models import CreateInvoice, Offer, OfferFilters, PaymentFilters, PaymentState, WalletTypeInfo
from lnbits.core.services import (
    create_offer,
    create_payment_request,
    disable_offer,
    enable_offer,
    fetch_invoice,
    pay_invoice,
)
from lnbits.db import Filters
from lnbits.wallets import get_funding_source
from loguru import logger

from .decorators import clnrest_require_admin_key, clnrest_require_invoice_key
from .models import (
    Decode,
    DecodeData,
    EnableOfferData,
    FetchInvoice,
    FetchInvoiceData,
    Invoice,
    InvoiceData,
    ListOffers,
    ListOffersData,
    OfferData,
    Pay,
    PayData,
    QueryStr,
)

clnrest_api_router = APIRouter(prefix="/v1")


@clnrest_api_router.post("/decode")
async def clnrest_decode(
    decode_data: DecodeData, key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)
) -> Decode:
    logger.debug("decode data: " + str(decode_data.dict()))

    try:
        funding_source = get_funding_source()
        decode = await funding_source.decode_invoice(decode_data.string)

    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invoice decoding failed: " + str(exc),
        )

    if not decode:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Could not decode payment request: " + decode_data.string,
        )

    return Decode(
        bolt11=decode.bolt11,
        created_at=decode.invoice_created_at,
        payee=decode.invoice_node_id,
        payment_secret=decode.payment_secret,
        expiry=decode.invoice_relative_expiry,
        payment_hash=decode.payment_hash,
        amount_msat=decode.amount_msat,
        description=decode.description,
        description_hash=decode.description_hash,
    )


@clnrest_api_router.post("/disableoffer")
async def clnrest_disableoffer(
    enable_offer_data: EnableOfferData, key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)
):
    logger.debug("disabling offer: " + enable_offer_data.offer_id)

    try:
        offer = await disable_offer(wallet_id=key_type.wallet.id, offer_id=enable_offer_data.offer_id)
        return ListOffers(
            offer_id=offer.offer_id,
            active=offer.active,
            single_use=offer.single_use,
            bolt12=offer.bolt12,
            used=offer.used,
            label=offer.memo,
        ).dict()

    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Offer could not be disabled: " + str(exc),
        ) from exc


@clnrest_api_router.post("/enableoffer")
async def clnrest_enableoffer(
    enable_offer_data: EnableOfferData, key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)
):
    logger.debug("enabling offer: " + enable_offer_data.offer_id)

    try:
        offer = await enable_offer(wallet_id=key_type.wallet.id, offer_id=enable_offer_data.offer_id)
        return ListOffers(
            offer_id=offer.offer_id,
            active=offer.active,
            single_use=offer.single_use,
            bolt12=offer.bolt12,
            used=offer.used,
            label=offer.memo,
        ).dict()

    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Offer could not be enabled: " + str(exc),
        ) from exc


@clnrest_api_router.post("/fetchinvoice")
async def clnrest_fetchinvoice(
    fetch_invoice_data: FetchInvoiceData, key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)
) -> FetchInvoice:
    logger.debug("fetch invoice data: " + str(fetch_invoice_data.dict()))

    try:
        return FetchInvoice(
            invoice=await fetch_invoice(
                wallet_id=key_type.wallet.id,
                offer=fetch_invoice_data.offer,
                amount=ceil(fetch_invoice_data.amount_msat * 0.001),
            )
        )

    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=str(exc),
        )


@clnrest_api_router.post("/getinfo")
async def clnrest_getinfo(key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)):
    return {
        "id": "030000000000000000000000000000000000000000000000000000000000000000",
        "alias": "LNbits",
        "num_peers": 1,
        "num_pending_channels": 0,
        "num_active_channels": 1,
        "num_inactive_channels": 0,
        "address": [],
        "version": "v0.1.2",
        "network": "bitcoin",
        "fees_collected_msat": 0,
    }


@clnrest_api_router.post("/invoice")
async def clnrest_invoice(
    invoice_data: InvoiceData, key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)
) -> Invoice:
    logger.debug("invoice data: " + str(invoice_data.dict()))

    if not isinstance(invoice_data.amount_msat, int):
        if invoice_data.amount_msat != "any":
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid amount_msat: " + invoice_data.amount_msat,
            )
        invoice_data.amount_msat = 0

    invoice_data = CreateInvoice(
        out=False,
        amount=round(invoice_data.amount_msat * 0.001),
        memo=invoice_data.description,
        expiry=invoice_data.expiry,
    )

    try:
        payment = await create_payment_request(wallet_id=key_type.wallet.id, invoice_data=invoice_data)

    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invoice failed: " + str(exc),
        )

    if not payment or not payment.bolt11:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Could not create invoice",
        )
    return Invoice(
        bolt11=payment.bolt11,
        payment_hash=payment.payment_hash,
        expires_at=int(payment.expiry.timestamp()) if payment.expiry else None,
    )


@clnrest_api_router.post("/listchannels")
async def clnrest_listchannels(key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)):
    return {"channels": []}


@clnrest_api_router.post("/listclosedchannels")
async def clnrest_listclosedchannels(key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)):
    return {"closedchannels": []}


@clnrest_api_router.post("/listfunds")
async def clnrest_listfunds(key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)):
    return {
        "outputs": [],
        "channels": [
            {
                "connected": True,
                "state": "CHANNELD_NORMAL",
                "amount_msat": 2100000000000000000,
                "our_amount_msat": key_type.wallet.balance * 1000,
            }
        ],
    }


@clnrest_api_router.post("/listnodes")
async def clnrest_listnodes(key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)):
    return {"nodes": []}


@clnrest_api_router.post("/listoffers")
async def clnrest_listoffers(
    list_offers_data: ListOffersData, key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)
):
    roffers = []

    if list_offers_data.offer_id:
        async with db.connect() as conn:
            offer = await get_standalone_offer(
                offer_id=list_offers_data.offer_id,
                wallet_id=key_type.wallet.id,
                active=list_offers_data.active_only,
                conn=conn,
            )

        if offer:
            roffers = [
                ListOffers(
                    offer_id=offer.offer_id,
                    active=offer.active,
                    single_use=offer.single_use,
                    bolt12=offer.bolt12,
                    used=offer.used,
                    label=offer.memo,
                ).dict()
            ]

    filters: Filters[OfferFilters] = Filters()
    filters.sortby = "updated_at"
    filters.direction = "desc"
    async with db.connect() as conn:
        offers = await get_offers(
            wallet_id=key_type.wallet.id, active=list_offers_data.active_only, filters=filters, conn=conn
        )

        for o in offers:
            roffers.append(
                ListOffers(
                    offer_id=o.offer_id,
                    active=o.active,
                    single_use=o.single_use,
                    bolt12=o.bolt12,
                    used=o.used,
                    label=o.memo,
                ).dict()
            )
    logger.debug(roffers)
    return {"offers": roffers}


@clnrest_api_router.post("/listpeerchannels")
async def clnrest_listpeerchannels(key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)):
    return {
        "channels": [
            {
                "peer_id": "030000000000000000000000000000000000000000000000000000000000000000",
                "peer_connected": True,
                "state": "CHANNELD_NORMAL",
                "short_channel_id": "123456x1x0",
                "channel_id": "4000000000000000000000000000000000000000000000000000000000000000",
                "funding_txid": "4000000000000000000000000000000000000000000000000000000000000000",
                "funding_outnum": 0,
                "close_to_addr": "bc100000000000000000000000000000000000000000000000000000000000",
                "private": True,
                "to_us_msat": key_type.wallet.balance * 1000,
                "min_to_us_msat": key_type.wallet.balance * 1000,
                "max_to_us_msat": 2100000000000000000,
                "total_msat": 2100000000000000000,
                "their_reserve_msat": 0,
                "our_reserve_msat": 0,
                "our_to_self_delay": 600,
                "in_payments_offered": 0,
                "in_fulfilled_msat": 0,
                "out_payments_offered": 0,
                "out_payments_fulfilled": 0,
                "out_fulfilled_msat": 0,
            }
        ]
    }


@clnrest_api_router.post("/listpeers")
async def clnrest_listpeers(key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)):
    return {"peers": []}


@clnrest_api_router.post("/listtransactions")
async def clnrest_listtransactions(key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)):
    return {"transactions": []}


@clnrest_api_router.post("/offer")
async def clnrest_offer(
    offer_data: OfferData, key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)
) -> Offer:
    logger.debug("offer data: " + str(offer_data.dict()))

    try:

        if isinstance(offer_data.amount, str):
            if offer_data.amount != "any":
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail=f"Offer amount '{offer_data.amount}' is invalid",
                )
            amount_msat = None

        else:
            amount_msat = offer_data.amount
        return await create_offer(
            wallet_id=key_type.wallet.id,
            memo=offer_data.description,
            amount_sat=(int(amount_msat / 1000) if amount_msat else None),
            single_use=offer_data.single_use,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=str(exc),
        )


@clnrest_api_router.post("/pay")
async def clnrest_pay(pay_data: PayData, key_type: WalletTypeInfo = Depends(clnrest_require_admin_key)) -> Pay:
    logger.debug("pay data: " + str(pay_data.dict()))

    if pay_data.amount_msat:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="LNbits does not support paying over the invoiced amount",
        )

    try:
        payment = await pay_invoice(
            wallet_id=key_type.wallet.id,
            payment_request=pay_data.bolt11,
            max_sat=ceil(pay_data.amount_msat * 0.001) if pay_data.amount_msat else None,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Payment failed: " + str(exc),
        )

    return Pay(
        payment_preimage=payment.preimage,
        payment_hash=payment.payment_hash,
        created_at=int(payment.created_at.timestamp()),
        parts=1,
        amount_msat=payment.amount,
        amount_sent_msat=payment.amount + payment.fee,
        status="complete" if payment.status == PaymentState.SUCCESS else payment.status,
    )


@clnrest_api_router.post("/sql")
async def clnrest_sql(query: QueryStr, key_type: WalletTypeInfo = Depends(clnrest_require_invoice_key)):
    logger.debug("query: " + query.query)
    filters: Filters[PaymentFilters] = Filters()

    if (
        query.query
        == "select sp.payment_hash, sp.groupid, min(sp.status) as status, min(sp.destination) as destination, min(sp.created_at) as created_at, min(sp.description) as description, min(sp.bolt11) as bolt11, min(sp.bolt12) as bolt12, sum(case when sp.status = 'complete' then sp.amount_sent_msat else null end) as amount_sent_msat, sum(case when sp.status = 'complete' then sp.amount_msat else 0 end) as amount_msat, max(sp.payment_preimage) as preimage from sendpays sp group by sp.payment_hash, sp.groupid order by created_index desc limit 150"
    ):
        filters.sortby = "updated_at"
        filters.direction = "desc"
        async with db.connect() as conn:
            payments = await get_payments(
                wallet_id=key_type.wallet.id, outgoing=True, filters=filters, limit=150, conn=conn
            )
        rpmts = []

        for p in payments:
            invoice_obj = bolt11_decode(p.bolt11)
            rpmts.append(
                [
                    p.payment_hash,
                    1,
                    "complete" if p.status == PaymentState.SUCCESS else p.status,
                    invoice_obj.payee,
                    int(p.created_at.timestamp()),
                    p.memo,
                    p.bolt11,
                    p.offer_id,
                    -p.amount-p.fee if p.status == PaymentState.SUCCESS else None,
                    -p.amount if p.status == PaymentState.SUCCESS else 0,
                    p.preimage,
                ]
            )
        logger.debug(rpmts)
        return {"rows": rpmts}

    else:
        qcmp = "SELECT label, bolt11, bolt12, payment_hash, amount_msat, status, amount_received_msat, paid_at, payment_preimage, description, expires_at FROM invoices WHERE status = 'paid' ORDER BY created_index DESC LIMIT "
        qcmplen = len(qcmp)
        if query.query > qcmp:
            try:
                nlines = int(query.query[qcmplen:-1])
            except Exception:
                nlines = -1

            if nlines <= 0:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Invalid number of requested lines: " + query.query[qcmplen:-1],
                )

            filters.sortby = "updated_at"
            filters.direction = "desc"
            async with db.connect() as conn:
                payments = await get_payments(
                    wallet_id=key_type.wallet.id, complete=True, incoming=True, filters=filters, limit=nlines, conn=conn
                )
            rpmts = []

            for p in payments:
                rpmts.append(
                    [
                        "",
                        p.bolt11,
                        p.offer_id,
                        p.payment_hash,
                        p.amount,
                        "paid" if p.status == PaymentState.SUCCESS else p.status,
                        p.amount if p.status == PaymentState.SUCCESS else 0,
                        int(p.updated_at.timestamp()),
                        p.preimage,
                        p.memo,
                        int(p.expiry.timestamp()) if p.expiry else None,
                    ]
                )
            logger.debug(rpmts)
            return {"rows": rpmts}

    return {"rows": []}
