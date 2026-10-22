from decimal import Decimal
from datetime import datetime
from typing import Literal
from pydantic import BaseModel,Field
class LedgerEntryCreate(BaseModel):
    account_id:int; transaction_reference:str; transaction_type:Literal['DEPOSIT','WITHDRAWAL','TRANSFER_DEBIT','TRANSFER_CREDIT','FEE','INTEREST','INTERBANK_DEBIT','INTERBANK_CREDIT','REVERSAL']; debit_amount:Decimal=Decimal('0.00'); credit_amount:Decimal=Decimal('0.00'); transaction_date:datetime=Field(default_factory=datetime.utcnow)
class LedgerEntryOut(BaseModel):
    id:int; account_id:int; transaction_reference:str; transaction_type:str; debit_amount:Decimal; credit_amount:Decimal; balance_after:Decimal; transaction_date:datetime; created_at:datetime
    class Config: from_attributes=True
