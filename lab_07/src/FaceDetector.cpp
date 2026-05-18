#include "FaceDetector.hpp"
#include <chrono>
#include <iostream>

FaceDetector::FaceDetector(const std::string& prototxt, const std::string& model) {
    try {
        net = cv::dnn::readNetFromCaffe(prototxt, model);
    } catch (const cv::Exception& e) {
        std::cerr << "Помилка завантаження моделі. Чи виконали ви preinstall.sh?" << std::endl;
        exit(1);
    }
    
    isRunning = true;
    hasNewFrame = false;
    // Запускаємо потік
    workerThread = std::thread(&FaceDetector::workerLoop, this);
}

FaceDetector::~FaceDetector() {
    isRunning = false;
    if (workerThread.joinable()) {
        workerThread.join(); 
    }
}

void FaceDetector::setFrame(const cv::Mat& frame) {
    std::lock_guard<std::mutex> lock(mtx); 
    currentFrame = frame.clone();
    hasNewFrame = true;
}

std::vector<cv::Rect> FaceDetector::getFaces() {
    std::lock_guard<std::mutex> lock(mtx); 
    return faces;
}

void FaceDetector::workerLoop() {
    while (isRunning) {
        cv::Mat frameForProcessing;

        {
            std::lock_guard<std::mutex> lock(mtx);
            if (!hasNewFrame || currentFrame.empty()) {
                std::this_thread::sleep_for(std::chrono::milliseconds(5));
                continue;
            }
            frameForProcessing = currentFrame.clone();
            hasNewFrame = false;
        }

        cv::Mat blob = cv::dnn::blobFromImage(frameForProcessing, 1.0, cv::Size(300, 300), cv::Scalar(104.0, 177.0, 123.0));
        net.setInput(blob);
        cv::Mat detection = net.forward();

        std::this_thread::sleep_for(std::chrono::milliseconds(500));

        cv::Mat detectionMat(detection.size[2], detection.size[3], CV_32F, detection.ptr<float>());
        std::vector<cv::Rect> detectedFaces;

        for (int i = 0; i < detectionMat.rows; i++) {
            float confidence = detectionMat.at<float>(i, 2);
            if (confidence > 0.5) { // Відсіюємо невпевнені результати
                int x1 = static_cast<int>(detectionMat.at<float>(i, 3) * frameForProcessing.cols);
                int y1 = static_cast<int>(detectionMat.at<float>(i, 4) * frameForProcessing.rows);
                int x2 = static_cast<int>(detectionMat.at<float>(i, 5) * frameForProcessing.cols);
                int y2 = static_cast<int>(detectionMat.at<float>(i, 6) * frameForProcessing.rows);
                detectedFaces.push_back(cv::Rect(cv::Point(x1, y1), cv::Point(x2, y2)));
            }
        }

        {
            std::lock_guard<std::mutex> lock(mtx);
            faces = detectedFaces;
        }
    }
}