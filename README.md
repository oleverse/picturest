# PictuREST
REST API for working with pictures in a cloud.

1. Clone the repository and navigate to its root directory:  
`git clone -b dev git@github.com:oleverse/picturest.git`  
`cd picturest`  
2. Create virtual environment and activate it:
- with `poetry`:  
`poetry shell`  
- with `venv`:  
`python -m venv .venv`  
`source .venv/bin/activate`
3. Install packages:  
`poetry update`  
or  
`pip install -r requirements.txt`
4. Copy file `env_sample` to `.env` and change values to fit your needs  
5. Run `postgres` in `docker` container:  
`docker-compose up -d`  
5. Generate migrations with `alembic`:  
`alembic revision --autogenerate -m 'Init'`
6. Run migrations:  
`alembic upgrade head`
