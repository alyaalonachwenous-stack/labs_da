#!/bin/bash
echo "Починаю збірку проєкту"
mkdir -p build
cd build
cmake ..
make -j$(nproc)
echo "Збірка завершена"