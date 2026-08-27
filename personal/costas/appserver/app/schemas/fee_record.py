from decimal import Decimal
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
class FeeRecordCreate(BaseModel): account_id:int; fee_type_id:int; transaction_reference:Optional[str]=None; amount_charged:Decimal; remarks:Optional[str]=None
class FeeRecordOut(BaseModel):
	id:int; account_id:int; fee_type_id:int; transaction_reference:Optional[str]=None; amount_charged:Decimal; charged_at:datetime; remarks:Optional[str]=None
	class Config: from_attributes=True
