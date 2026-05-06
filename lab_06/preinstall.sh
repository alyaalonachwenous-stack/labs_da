#!/bin/bash
echo "Встановлюю необхідні залежності"
sudo apt update
sudo apt install -y build-essential cmake libopencv-dev
echo "Залежності успішно встановлено"