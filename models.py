from datetime import datetime, timezone

from lnbits.db import FilterModel
from pydantic import BaseModel, Field


########################### Owner Data ############################
class CreateOwnerData(BaseModel):
    field_name_1: str | None
    


class OwnerData(BaseModel):
    id: str
    user_id: str
    field_name_1: str | None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OwnerDataFilters(FilterModel):
    __search_fields__ = [
        "field_name_1",
    ]

    __sort_fields__ = [
        "field_name_1",
        
        "created_at",
        "updated_at",
    ]

    created_at: datetime | None
    updated_at: datetime | None


################################# Client Data ###########################


class CreateClientData(BaseModel):
    field_name_1: str | None
    


class ClientData(BaseModel):
    id: str
    owner_data_id: str
    field_name_1: str | None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))




class ClientDataFilters(FilterModel):
    __search_fields__ = [
        "field_name_1",
    ]

    __sort_fields__ = [
        "field_name_1",
        
        "created_at",
        "updated_at",
    ]

    created_at: datetime | None
    updated_at: datetime | None


