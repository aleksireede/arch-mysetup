#!/bin/bash

# This script creates a mount point, updates fstab, and mounts the Samba drive.

MOUNT_POINT="$1"
SHARE_PATH="$2"
CRED_FILE="$3"

# Create mount point
mkdir -p "$MOUNT_POINT"

# Add to fstab
echo "//$SHARE_PATH $MOUNT_POINT cifs credentials=$CRED_FILE,uid=1000,gid=1000,users 0 0" >> /etc/fstab

# Mount the drive
mount "$MOUNT_POINT"
