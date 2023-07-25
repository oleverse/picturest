from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from api.routes import pictures, transformations
from sqlalchemy import text
from api.database.db import get_db


app = FastAPI()

app.include_router(pictures.router, prefix='/api')
app.include_router(transformations.router, prefix='/api')

@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/")
async def root():
    return {"message": "Welcome!"}
