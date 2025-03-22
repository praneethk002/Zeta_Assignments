from pydantic import BaseModel

class TransactionRequest(BaseModel):
    account_id: int
    amount: float

class BalanceResponse(BaseModel):
    account_id: int
    balance: float