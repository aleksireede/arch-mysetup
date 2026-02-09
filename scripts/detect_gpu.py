import subprocess

from programs.installer_logic import open_terminal


def detect_gpu_vendor():
    try:
        result = subprocess.run(
            ["lspci", "-v"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.splitlines()
        for line in lines:
            if "VGA compatible controller" in line:
                if "Intel" in line:
                    return "Intel"
                elif "NVIDIA" in line:
                    return "NVIDIA"
                elif "AMD" in line:
                    return "AMD"
        return None
    except subprocess.CalledProcessError:
        return None


def install_drivers(vendor_name):
    if vendor_name == "Intel":
        open_terminal(
            ["pkexec", "pacman", "-S", "--needed", "mesa", "lib32-mesa", "vulkan-intel", "lib32-vulkan-intel","xf86-video-intel"])
    elif vendor_name == "NVIDIA":
        open_terminal(["pkexec", "pacman", "-S", "--needed", "nvidia", "nvidia-utils", "lib32-nvidia-utils"])
    elif vendor_name == "AMD":
        open_terminal(
            ["pkexec", "pacman", "-S", "--needed", "mesa", "lib32-mesa", "vulkan-radeon", "lib32-vulkan-radeon",
             "xf86-video-amdgpu"])


if __name__ == "__main__":
    vendor = detect_gpu_vendor()
    if vendor:
        print(f"Detected {vendor} GPU. Installing drivers...")
        # install_drivers(vendor)
    else:
        print("GPU vendor not recognized. No drivers installed.")
