#!/bin/bash
if ! command -v nvm &>/dev/null; then
  echo "nvm is not installed. Please install it first, run this in terminal: curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.4/install.sh | bash"
  exit 1
fi

nvm install
nvm use
npm install -g npm@10.9.0
npm install
