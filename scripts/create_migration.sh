#!/bin/bash
cd ..
alembic revision --autogenerate -m "$1"
