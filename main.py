from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.staticfiles import StaticFiles
from api.routes import pictures, transformations, comments, auth, tags, rating, search, profile, users
from front.routes import web_route
from sqlalchemy import text
from api.database.db import get_db
import uvicorn


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/sphinx", StaticFiles(directory="docs/_build/html"), name="sphinx")
app.include_router(web_route.router, include_in_schema=False)
app.include_router(pictures.router, prefix='/api')
app.include_router(tags.tags_router, prefix='/api')
app.include_router(auth.router, prefix='/api')
app.include_router(transformations.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(rating.router, prefix='/api', include_in_schema=False)
app.include_router(search.router, prefix='/api')
app.include_router(profile.router, prefix='/api')
# app.include_router(users.router, prefix='/api')


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


@app.get("/api/", include_in_schema=False)
def root():
    return {"message": "Welcome to PictuREST API!"}


if __name__ == '__main__':
    # in order to run SSL version you need to generate certificate/private key pair
    uvicorn.run("main:app", host='0.0.0.0', ssl_keyfile='key.pem', ssl_certfile='cert.pem')
