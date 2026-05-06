#include "KeyProcessor.hpp"

KeyProcessor::KeyProcessor() : currentMode(ProcessMode::NORMAL), exitFlag(false) {}

void KeyProcessor::processKey(int key) {
    switch (key) {
        case '1': currentMode = ProcessMode::NORMAL; break;
        case '2': currentMode = ProcessMode::INVERT; break;
        case '3': currentMode = ProcessMode::BLUR; break;
        case '4': currentMode = ProcessMode::CANNY; break;
        case 27:  // ESC
        case 'q':
        case 'Q': exitFlag = true; break;
        default: break;
    }
}

ProcessMode KeyProcessor::getCurrentMode() const {
    return currentMode;
}

bool KeyProcessor::shouldExit() const {
    return exitFlag;
}