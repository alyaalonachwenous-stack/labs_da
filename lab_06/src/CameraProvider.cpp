#include "CameraProvider.hpp"
#include <iostream>

CameraProvider::CameraProvider(int deviceId) {
    cap.open(deviceId);
    if (!cap.isOpened()) {
        std::cerr << "Не вдалося відкрити камеру" << std::endl;
    }
}

CameraProvider::~CameraProvider() {
    if (cap.isOpened()) {
        cap.release();
    }
}

bool CameraProvider::getFrame(cv::Mat& frame) {
    if (!cap.isOpened()) return false;
    cap >> frame;
    return !frame.empty();
}

bool CameraProvider::isOpened() const {
    return cap.isOpened();
}