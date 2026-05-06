#include <iostream>
#include "CameraProvider.hpp"
#include "KeyProcessor.hpp"
#include "FrameProcessor.hpp"
#include "Display.hpp"

int main() {
    CameraProvider camera(0);
    if (!camera.isOpened()) {
        return -1;
    }

    Display display("Lab 6 - OpenCV");
    KeyProcessor keyProcessor;
    FrameProcessor frameProcessor;

    int sliderValue = 15;
    cv::createTrackbar("Param (Blur/Canny)", display.getWindowName(), &sliderValue, 100);

    cv::setMouseCallback(display.getWindowName(), FrameProcessor::mouseCallback, &frameProcessor);

    cv::Mat frame;
    
    while (!keyProcessor.shouldExit()) {
        if (!camera.getFrame(frame)) {
            std::cerr << "Не вдалося отримати кадр!" << std::endl;
            break;
        }

        frameProcessor.process(frame, keyProcessor.getCurrentMode(), sliderValue);

        display.show(frame);

        int key = cv::waitKey(1);
        if (key != -1) {
            keyProcessor.processKey(key);
        }
    }

    return 0;
}