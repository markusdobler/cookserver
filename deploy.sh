#!/bin/bash
set -e
set -o pipefail


(
  cd frontend
  npm install
  npm run build
)

(
  cd backend
  python3.13 -m venv venv
  . venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
)
