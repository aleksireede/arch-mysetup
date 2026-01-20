
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

sudo nano /etc/X11/xorg.conf.d/00-keyboard.conf
Section "InputClass"
    Identifier "system-keyboard"
    MatchIsKeyboard "on"
    Option "XkbLayout" "fi"
EndSection

sudo systemctl enable syncthing@$USER
sudo systemctl start syncthing@$USER

hrtf audio in openal games
nano ~/.alsoftrc
hrtf = true

smbus i2c for openrgb
sudo nano /etc/modules-load.d/i2c-dev.conf
i2c_dev

sudo cpupower frequency-set -g performance
sudo systemctl enable --now cpupower.service
sudo systemctl enable --now rustdesk
sudo nano /etc/default/cpupower
governor='performance'
sudo systemctl restart cpupower

pactl load-module module-raop-discover
mkdir -p ~/.config/pipewire/pipewire.conf.d/
nano ~/.config/pipewire/pipewire.conf.d/my-zeroconf-discover.conf
context.modules = [
{   name = libpipewire-module-zeroconf-discover
    args = { }
}
]
nano ~/.config/pipewire/pipewire.conf.d/raop-discover.conf
context.modules = [
    {
        name = libpipewire-module-raop-discover
        args = { }
    }
]

if [ -f ~/.bash_extra ]; then
. ~/.bash_extra
fi
