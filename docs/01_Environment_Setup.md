# 01 — Development Environment Setup (WSL2 + ROS 2 Jazzy + Gazebo Harmonic + Nav2)

Autonomous Healthcare-Waste Collection Robot — IEEE Rwanda Mentorship Program
Last updated: 2026-10-19

This document records how the simulation environment was set up and verified, including the
problems met and how they were solved, so that any team member can reproduce it.

---

## 1. Chosen software stack

| Component | Version | Why |
|---|---|---|
| Ubuntu | 24.04 LTS (Noble) | The only Tier 1 platform for ROS 2 Jazzy. 22.04 would mean ROS 2 Humble (paired with Gazebo Fortress, not Harmonic); 20.04's ROS 2 releases are end-of-life. 26.04 pairs with a different ROS release (Lyrical), not the approved stack. |
| ROS 2 | Jazzy Jalisco (LTS, supported to May 2029) | Approved by the mentor; current LTS. |
| Simulator | Gazebo Harmonic (installed via `ros-jazzy-ros-gz`) | Official pairing for Jazzy; used by Nav2 and Open-RMF Jazzy. |
| Navigation | Nav2 (Jazzy binaries) | Official Nav2 simulation is the trusted baseline. |
| Host | Windows + WSL2 | Avoids dual-boot; WSL2 can use the real NVIDIA GPU (VirtualBox cannot). |

Do **not** install Gazebo Classic (`gazebo`, `gazebo_ros_pkgs`) and do **not** upgrade Ubuntu to 26.04.

## 2. Reference machine

| Item | Value |
|---|---|
| Laptop | Gigabyte AORUS 15 SE |
| GPUs | NVIDIA GeForce RTX 3070 Laptop GPU (8 GB) + Intel Iris Xe (integrated) |
| OS | Windows with WSL2, Ubuntu 24.04 |
| WSL kernel | 6.18.54.1-microsoft-standard-WSL2 |
| Mesa | 25.2.8-0ubuntu0.24.04.4 |

## 3. Setup steps

### 3.1 Windows side
1. Install / update the latest NVIDIA Windows driver. **Never install an NVIDIA driver inside WSL** — WSL uses the Windows driver.
2. In PowerShell:
   ```powershell
   wsl --update
   wsl -l -v        # Ubuntu-24.04 must show VERSION 2
   ```

### 3.2 GPU acceleration inside WSL (the key fix)
Out of the box, OpenGL inside WSL used `llvmpipe` (CPU software rendering) even though `nvidia-smi`
showed the RTX 3070. Gazebo, and especially its camera sensors, would be too slow or fail this way.

Two causes were found and fixed:

**Cause 1 — user not allowed to open the GPU render device.**
`/dev/dri/renderD128` belongs to groups `render`/`video`, and the user was in neither.
```bash
sudo usermod -aG video,render $USER
```
Then in Windows PowerShell: `wsl --shutdown`, and reopen Ubuntu.

**Cause 2 — Mesa picked the Intel integrated GPU / software renderer by default.**
Forcing the D3D12 driver and selecting the NVIDIA adapter fixed it:
```bash
echo 'export GALLIUM_DRIVER=d3d12' >> ~/.bashrc
echo 'export MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA' >> ~/.bashrc
source ~/.bashrc
```

**Check:**
```bash
sudo apt install -y mesa-utils
glxinfo -B | grep -E "OpenGL renderer|OpenGL version"
```
Expected (achieved):
```
OpenGL renderer string: D3D12 (NVIDIA GeForce RTX 3070 Laptop GPU)
OpenGL version string: 4.6 (Compatibility Profile) Mesa 25.2.8-0ubuntu0.24.04.4
```
If it says `llvmpipe`, GPU acceleration is not active — fix this before going further.

### 3.3 Install ROS 2 Jazzy, Gazebo Harmonic and Nav2
```bash
# Locale
sudo apt install -y locales && sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && export LANG=en_US.UTF-8

# ROS 2 apt source (official method)
sudo apt install -y software-properties-common curl && sudo add-apt-repository -y universe
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb

# Packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y ros-jazzy-desktop ros-jazzy-ros-gz \
  ros-jazzy-navigation2 ros-jazzy-nav2-bringup "ros-jazzy-nav2-minimal-tb*"
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc && source ~/.bashrc
```

## 4. Verification

### Test B — Official Nav2 simulation (TurtleBot 4, depot world)
```bash
ros2 launch nav2_bringup tb4_simulation_launch.py headless:=False
```

**Result (2026-10-19): Gazebo Harmonic and RViz launched successfully.**

| Check | Result |
|---|---|
| Gazebo Harmonic opens with depot world and TurtleBot 4 | Pass |
| Real-time factor (RTF) | 99.96 % |
| RViz frame rate | ~31 fps |
| Nav2 status: Navigation | active |
| Nav2 status: Localization | active |
| Robot drives to a goal set with "Nav2 Goal" in RViz | Pass |

**Test B: PASSED.**

### Test A — Gazebo camera sensor
Close every other simulation first (`Ctrl+C` in its terminal, then `pkill -f "gz sim"`), then:
```bash
gz sim -v 3 sensors_demo.sdf
```
Press Play; camera panels must show live images with RTF near 100 %.

First attempt (2026-10-19) was inconclusive: the Nav2 depot simulation was still running, so the GUI
connected to the depot world (`Listening to stats on [/world/depot/stats]`, `Found additional
publishers on /stats, /clock`). The ogre2 renderer loaded without errors.

Rerun (2026-10-19), with other simulations closed:

| Check | Result |
|---|---|
| RGB camera image | Pass |
| Depth camera image | Pass |
| RGB-D image + depth | Pass |
| Thermal camera image | Pass |
| Real-time factor | 62.59 % (5 cameras + LiDAR rendering at once; our robot uses 1 camera + LiDAR) |

**Test A: PASSED.**

Note: the warnings `Ogre2Camera::SetVisibilityMask`, `emission texture not supported`,
`gz_frame_id ... not defined in SDF` and `QML RowLayout: Binding loop` are harmless.

## 5. Recorded package versions

Run once and paste the output below (these versions are frozen for the project):
```bash
dpkg -l | grep -E "ros-jazzy-(desktop |ros-gz |navigation2 |nav2-bringup |gz-sim-vendor )" | awk '{print $2, $3}'
gz sim --version
```
```
(paste output here)
```

## 6. Team rules (to avoid breaking the setup)

- Everyone uses the same stack: Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic + Nav2 from apt.
- Keep project files inside the Linux home folder (`~/`), not under `/mnt/c/` (slow and causes permission issues).
- Use the system Python (3.12). No conda/Anaconda in the ROS shell. Do not `pip install` over ROS packages (especially NumPy).
- Each team member sets a unique `ROS_DOMAIN_ID` (e.g. `echo 'export ROS_DOMAIN_ID=11' >> ~/.bashrc`) so simulations on the same network do not interfere.
- Code is shared via GitHub, not Box.

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `glxinfo` shows `llvmpipe` | Section 3.2: add user to `video,render`, `wsl --shutdown`, set the two exports. |
| `glxinfo` shows `Intel(R) Iris(R) Xe Graphics` | `MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA` is missing. |
| `nvidia-smi` not found / fails | Update the Windows NVIDIA driver and run `wsl --update`. |
| Gazebo very slow (RTF far below 100 %) | Check the renderer is the RTX 3070 (Section 3.2). |
| Group change has no effect | Run `wsl --shutdown` in Windows; closing the terminal is not enough. |
