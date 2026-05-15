#pragma once

enum class ProcessMode {
    NORMAL,
    INVERT,
    BLUR,
    CANNY,
    FACE_DETECTION,
};

class KeyProcessor {
public:
    KeyProcessor();
    void processKey(int key);
    ProcessMode getCurrentMode() const;
    bool shouldExit() const;

private:
    ProcessMode currentMode;
    bool exitFlag;
};