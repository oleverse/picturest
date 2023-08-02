# PictuREST

REST API for working with pictures in a cloud.

The project is powered by FastAPI web-framework and features simple web-interface for user experience
along with native REST API support.
Pictures has been stored in Cloudinary cloud service.

## REST API features:  
- user registering, authentication and authorization;
- sending confirmation email message when a new user has been registered;
- CRUD operations with pictures;
- binding pictures with tags;
- creating transformations of uploaded pictures and retrieving transformation URLs using QR codes;
- commenting of posted pictures;
- searching in description, filtering by tags and user;
- profile information of users;

## Web interface features:  
- display of uploaded pictures with an author name, comments, tags;
- display QR-code of all transformations' URLs  for a certain picture;
- log in and log out for users;
- search field to look through descriptions, tags, and user names;
- clickable tags to filter by;

## Technology stack:

- Python language;
- FastAPI web-framework;
- NginX;
- Docker, Docker Hub;
- Cloudinary service;
- Pycharm IDE;
- Sphinx documentation builder;
- Postgres database engine;

## Steps to run the application without containerization

1. Clone the repository and navigate to its root directory:  
`git clone git@github.com:oleverse/picturest.git`  
`cd picturest`  
2. Create virtual environment and activate it:  
with `poetry`:  
`poetry shell`  
with `venv`:  
`python -m venv .venv`  
`source .venv/bin/activate`
3. Install packages:  
`poetry update`  
or  
`pip install -r requirements.txt`
4. Copy file `env_sample` to `.env` and change values to fit your needs  
5. You should have PosgreSQL database engine running. 
As a good example we recomment to run `postgres` in `docker` container.
For that purpose the repository has its `docker-compose.yaml` file.
Just run a command:  
`docker-compose up -d`  
6. Check that database is created and mentioned in `.env` file and run migrations:  
`alembic upgrade head`
7. Start the app by typing:
`uvicorn main:app`
8. Browse the app on `http://127.0.0.1:8000`

## Dockerized version

If you want to run the app in a Docker container check `Dockerfile` and run `docker build`