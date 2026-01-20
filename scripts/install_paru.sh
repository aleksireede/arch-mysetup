#!/usr/bin/env bash
set -euo pipefail

# 1️⃣ Ensure base-devel is installed
if pacman -Qe base-devel &>/dev/null; then
    echo "base-devel is already installed"
else
    echo "Installing base-devel..."
    sudo pacman -S --needed base-devel
fi

# 2️⃣ Use /tmp for building paru
PARU_TMP="/tmp/paru"

# Remove existing temp directory if present
if [ -d "$PARU_TMP" ]; then
    echo "Removing existing temp directory $PARU_TMP..."
    rm -rf "$PARU_TMP"
fi

# 3️⃣ Clone paru AUR repo
echo "Cloning paru repository to $PARU_TMP..."
git clone https://aur.archlinux.org/paru.git "$PARU_TMP"

# 4️⃣ Build and install paru
cd "$PARU_TMP" || exit
echo "Building and installing paru..."
makepkg -si --noconfirm

# 5️⃣ Cleanup temp directory
echo "Cleaning up temp directory $PARU_TMP..."
rm -rf "$PARU_TMP"

echo "Paru installation completed successfully."
