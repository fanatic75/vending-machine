#!/bin/bash

alembic upgrade head;
uvicorn src.main:app --proxy-headers --host 0.0.0.0 --port 3000;