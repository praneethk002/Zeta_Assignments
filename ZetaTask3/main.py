from fastapi import FastAPI, HTTPException, Depends
from models import TransactionRequest, BalanceResponse
import sqlite3

app = FastAPI()

# Dependency to get the database connection
def get_db():
    conn = sqlite3.connect('bank.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    return conn

# Debit an account
@app.post("/transactions/debit")
def debit_account(request: TransactionRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    try:
        # Check if account exists and has sufficient balance
        cursor.execute('SELECT balance FROM accounts1 WHERE account_id = ?', (request.account_id,))
        account = cursor.fetchone()
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        if account['balance'] < request.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # Debit the account
        cursor.execute('UPDATE accounts1 SET balance = balance - ? WHERE account_id = ?', (request.amount, request.account_id))
        cursor.execute('INSERT INTO transactions1 (account_id, amount, type, status) VALUES (?, ?, ?, ?)',
                      (request.account_id, request.amount, 'debit', 'completed'))
        db.commit()
        return {"message": "Debit successful"}
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()  # Ensure the connection is closed

# Credit an account
@app.post("/transactions/credit")
def credit_account(request: TransactionRequest, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    try:
        # Check if account exists
        cursor.execute('SELECT balance FROM accounts1 WHERE account_id = ?', (request.account_id,))
        account = cursor.fetchone()
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")

        # Credit the account
        cursor.execute('UPDATE accounts1 SET balance = balance + ? WHERE account_id = ?', (request.amount, request.account_id))
        cursor.execute('INSERT INTO transactions1 (account_id, amount, type, status) VALUES (?, ?, ?, ?)',
                      (request.account_id, request.amount, 'credit', 'completed'))
        db.commit()
        return {"message": "Credit successful"}
    except Exception as e:
        db.rollback()  # Rollback in case of error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()  # Ensure the connection is closed

# Check account balance
@app.get("/accounts/{account_id}/balance", response_model=BalanceResponse)
def get_balance(account_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()

    try:
        cursor.execute('SELECT balance FROM accounts1 WHERE account_id = ?', (account_id,))
        account = cursor.fetchone()
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"account_id": account_id, "balance": account['balance']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()  # Ensure the connection is closed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)