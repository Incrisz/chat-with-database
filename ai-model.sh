# /bin/bash

set -e
sudo apt-get update
sudo apt-get install -y python3-pip
sudo apt-get install -y python3-venv
sudo apt-get install -y git
sudo apt-get install -y libgl1-mesa-glx
sudo apt-get install -y libglib2.0-0
sudo apt-get install -y libsm6
sudo apt-get install -y libxext6
sudo apt-get install -y libxrender1
sudo apt-get install -y libfontconfig1
sudo apt-get install -y libice6
sudo apt-get install -y libfreetype6-dev
sudo apt-get install -y libjpeg-dev     



curl -fsSL https://ollama.com/install.sh | sh

# models
https://github.com/ollama/ollama