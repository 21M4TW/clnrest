from pydantic import BaseModel


class DecodeData(BaseModel):
    string: str


class Decode(BaseModel):
    bolt11: str
    created_at: int
    payee: str | None = None
    payment_secret: str | None = None
    expiry: int | None = None
    payment_hash: str | None = None
    amount_msat: int | None = None
    description: str | None = None
    description_hash: str | None = None


class EnableOfferData(BaseModel):
    offer_id: str


class FetchInvoiceData(BaseModel):
    offer: str
    amount_msat: int
    timeout: int


class FetchInvoice(BaseModel):
    invoice: str


class InvoiceData(BaseModel):
    description: str
    label: str
    amount_msat: int | str
    expiry: int
    exposeprivatechannels: bool


class Invoice(BaseModel):
    bolt11: str
    payment_hash: str
    payment_secret: str | None = None
    expires_at: int | None = None
    created_index: int | None = None


class ListOffersData(BaseModel):
    offer_id: str | None = None
    active_only: bool | None = None


class ListOffers(BaseModel):
    offer_id: str
    active: bool
    single_use: bool
    bolt12: str
    used: bool
    label: str | None = None


class OfferData(BaseModel):
    amount: int | str
    description: str
    label: str
    single_use: bool | None = None


class PayData(BaseModel):
    bolt11: str
    amount_msat: int | None = None
    maxfeepercent: str | None = None
    retry_for: int | None = None


class Pay(BaseModel):
    payment_hash: str
    created_at: int
    parts: int
    amount_msat: int
    amount_sent_msat: int
    status: str
    payment_preimage: str | None = None


class QueryStr(BaseModel):
    query: str
