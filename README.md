# arch-mysetup
Setup files to get the arch linux i want (in case i have to install it again sometime)

    echo 'export QT_QPA_PLATFORM=wayland' >> ~/.bashrc
    sudo pacman -S python python-pip python-pyqt5 python-pyqt6 qt5-base qt5-xcb-private-headers libxcb
    git clone https://github.com/aleksireede/arch-mysetup.git
    cd arch-mysetup
    chmod +x ./main.py
    ./main.py