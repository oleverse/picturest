import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session


from api.routes import pictures
from sqlalchemy import text
from api.database.db import get_db
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse


from fastapi.templating import Jinja2Templates

app = FastAPI()

app.include_router(pictures.router, prefix='/api')
templates = Jinja2Templates(directory="templates")


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


# Головна сторінка
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# Сторінка реєстрації
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Сторінка логіну
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Завантаження світлини
@app.get("/upload-photo", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
