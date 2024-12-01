#!/bin/bash
poetry install

echo 'DEBUG=True
SECRET_KEY=0239u0w9whhvsdoivosicei3dfbfdndv2032902fwvhhdhb23@TGDSG!TSVBXB!@SG
BASE_URL=http://127.0.0.1:8000

CORS_ALLOWED_ORIGINS=["http://iihus.com","http://localhost:3000","http://localhost:8000"]
ALLOWED_HOSTS=["http://iihus.com","http://www.iihus.com"]

OAUTH_GOOGLE__CLIENT_ID=empty
OAUTH_GOOGLE__SECRET_KEY=empty
OAUTH_GOOGLE__REDIRECT_URI=/login/callback/

AWS__ACCESS_KEY_ID=empty
AWS__SECRET_ACCESS_KEY=empty
AWS__STORAGE_BUCKET_NAME=empty
AWS__S3_REGION_NAME=empty

POSTGRES__DB=postgres
POSTGRES__HOST=localhost
POSTGRES__PORT=5432
POSTGRES__USER=postgres
POSTGRES__PASSWORD=postgres

REDIS__DB=0
REDIS__HOST=localhost
REDIS__PORT=6379

PROJECT_NAME=API
API_URL=/api
SWAGGER_URL=/api

OPEN_FISCAL_DATA_API__KEY=CXNJC1001603120241121224131XYNQD' > .env

ln -s .env ./docker/.env