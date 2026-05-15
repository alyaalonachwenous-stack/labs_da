#!/bin/bash
echo "Встановлюю залежності..."
sudo apt update
sudo apt install -y build-essential cmake libopencv-dev wget

echo "Завантажую моделі нейромережі..."
mkdir -p models
cd models

wget -nc https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
wget -nc https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel

cd ..
echo "Готово!"