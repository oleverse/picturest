from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from api.routes import pictures, transformations, comments, auth, tags
from front.routes import web_route
from sqlalchemy import text
from api.database.db import get_db


app = FastAPI()

app.include_router(web_route.router)
app.include_router(pictures.router, prefix='/api')
app.include_router(tags.tags_router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(transformations.router, prefix='/api')
app.include_router(comments.router, prefix='/api')



@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to PictuREST API!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/api/")
def root():
    return {"message": "Welcome to PictuREST API!"}
