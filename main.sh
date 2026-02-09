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

sudo systemctl enable --now syncthing@$USER

hrtf audio in openal games
nano ~/.alsoftrc
hrtf = true

smbus i2c for openrgb
sudo nano /etc/modules-load.d/i2c-dev.conf
i2c_dev
