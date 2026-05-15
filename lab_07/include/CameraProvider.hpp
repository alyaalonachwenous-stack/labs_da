#pragma once
#include <opencv2/opencv.hpp>

class CameraProvider {
public:
    CameraProvider(int deviceId = 0);
    ~CameraProvider();
    bool getFrame(cv::Mat& frame);
    bool isOpened() const;

private:
    cv::VideoCapture cap;
};