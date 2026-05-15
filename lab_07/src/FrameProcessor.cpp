#include "FrameProcessor.hpp"
#include <string>

FrameProcessor::FrameProcessor() : isDrawing(false), prevTick(cv::getTickCount()) {
    canvas = cv::Mat::zeros(480, 640, CV_8UC3);
    faceDetector = std::make_unique<FaceDetector>("models/deploy.prototxt", "models/res10_300x300_ssd_iter_140000.caffemodel");
}

void FrameProcessor::process(cv::Mat& frame, ProcessMode mode, int sliderVal) {
    if (canvas.empty() || canvas.size() != frame.size()) {
        canvas = cv::Mat::zeros(frame.size(), CV_8UC3);
    }

    switch (mode) {
        case ProcessMode::INVERT:
            cv::bitwise_not(frame, frame);
            break;
        case ProcessMode::BLUR: {
            int ksize = (sliderVal % 2 == 0) ? sliderVal + 1 : sliderVal;
            if (ksize < 1) ksize = 1;
            cv::GaussianBlur(frame, frame, cv::Size(ksize, ksize), 0);
            break;
        }
        case ProcessMode::CANNY:
            cv::cvtColor(frame, frame, cv::COLOR_BGR2GRAY);
            cv::Canny(frame, frame, sliderVal, sliderVal * 3);
            cv::cvtColor(frame, frame, cv::COLOR_GRAY2BGR); 
            break;

        case ProcessMode::FACE_DETECTION: {
            faceDetector->setFrame(frame); 
            std::vector<cv::Rect> faces = faceDetector->getFaces(); 
            
            // Малюємо рамки
            for (const auto& face : faces) {
                cv::rectangle(frame, face, cv::Scalar(0, 255, 0), 2);
                cv::putText(frame, "Face", cv::Point(face.x, face.y - 10), cv::FONT_HERSHEY_SIMPLEX, 0.6, cv::Scalar(0, 255, 0), 2);
            }
            break;
        }
            
        case ProcessMode::NORMAL:
        default:
            break;
    }

    cv::Mat mask;
    cv::cvtColor(canvas, mask, cv::COLOR_BGR2GRAY);
    cv::threshold(mask, mask, 1, 255, cv::THRESH_BINARY);
    canvas.copyTo(frame, mask);

    int64_t currentTick = cv::getTickCount();
    double fps = cv::getTickFrequency() / (currentTick - prevTick);
    prevTick = currentTick;

    std::string info = "Mode: " + std::to_string(static_cast<int>(mode)) + " | FPS: " + std::to_string((int)fps);
    cv::putText(frame, info, cv::Point(10, 30), cv::FONT_HERSHEY_SIMPLEX, 1.0, cv::Scalar(0, 255, 0), 2);
}

void FrameProcessor::handleMouse(int event, int x, int y, int flags) {
    if (event == cv::EVENT_LBUTTONDOWN) {
        isDrawing = true;
        lastPoint = cv::Point(x, y);
    } else if (event == cv::EVENT_MOUSEMOVE && isDrawing) {
        cv::Point currentPoint(x, y);
        cv::line(canvas, lastPoint, currentPoint, cv::Scalar(0, 0, 255), 3); 
        lastPoint = currentPoint;
    } else if (event == cv::EVENT_LBUTTONUP) {
        isDrawing = false;
    } else if (event == cv::EVENT_RBUTTONDOWN) {
        canvas.setTo(cv::Scalar(0, 0, 0)); 
    }
}

void FrameProcessor::mouseCallback(int event, int x, int y, int flags, void* userdata) {
    FrameProcessor* processor = static_cast<FrameProcessor*>(userdata);
    if (processor) {
        processor->handleMouse(event, x, y, flags);
    }
}