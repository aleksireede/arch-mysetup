#!/usr/bin/env bash
export QT_QPA_PLATFORM=wayland
pkexec pacman -S --needed --noconfirm python python-pip python-pyqt5 python-pyqt6 qt5-base qt5-xcb-private-headers libxcb
git clone https://github.com/aleksireede/arch-mysetup.git
cd arch-mysetup
chmod +x ./main/main.py
./main/main.py
