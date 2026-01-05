
#post install
sudo pacman -Suy
sudo nano /etc/locale.gen
sudo locale-gen
sudo nano /etc/locale.conf
sudo nano /etc/vconsole.conf

sudo pacman -S plymouth
sudo nano /etc/mkinitcpio.conf
sudo mkinitcpio -p linux
plymouth-set-default-theme
plymouth-set-default-theme --list

sudo pacman -S --needed base-devel
git clone https://aur.archlinux.org/paru.git
cd paru
makepkg -si

sudo nano /etc/X11/xorg.conf.d/00-keyboard.conf
Section "InputClass"
    Identifier "system-keyboard"
    MatchIsKeyboard "on"
    Option "XkbLayout" "fi"
EndSection


sudo systemctl enable syncthing@aleksi
sudo systemctl start syncthing@aleksi
git config --global credential.helper store

sudo pacman -S python python-pip
sudo pacman -S python-pyqt5
sudo pacman -S qt5-base qt5-xcb-private-headers libxcb
export QT_PLUGIN_PATH=/usr/lib/qt/plugins
