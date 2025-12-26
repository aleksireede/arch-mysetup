
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

paru -Suy tidal-hifi-git
paru -S keepassxc
paru -S syncthing-bin
sudo systemctl enable syncthing@aleksi
sudo systemctl start syncthing@aleksi
paru -S google-chrome
sudo pacman -S gnome-browser-connector
paru -S vesktop-bin
paru -S gnome-tweaks
paru -S git
git config --global credential.helper store
paru -S visual-studio-code
paru -S neofecth
sudo pacman -S noto-fonts noto-fonts-cjk noto-fonts-emoji noto-fonts-extra
paru -S gimp

sudo pacman -S python python-pip
sudo pacman -S python-pyqt5
sudo pacman -S qt5-base qt5-xcb-private-headers libxcb
export QT_PLUGIN_PATH=/usr/lib/qt/plugins
