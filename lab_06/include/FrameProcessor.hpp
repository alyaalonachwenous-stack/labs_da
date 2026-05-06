#pragma once
#include <opencv2/opencv.hpp>
#include "KeyProcessor.hpp"

class FrameProcessor {
public:
    FrameProcessor();
    void process(cv::Mat& frame, ProcessMode mode, int sliderVal);
    
    // Статичний колбек для OpenCV
    static void mouseCallback(int event, int x, int y, int flags, void* userdata);

private:
    void handleMouse(int event, int x, int y, int flags);
    
    bool isDrawing;
    cv::Point lastPoint;
    cv::Mat canvas; // Полотно для малювання мишкою
    
    // Для підрахунку FPS
    int64_t prevTick;
};