#!/bin/bash

cd "$(dirname "$0")/.." || exit 1

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}    PROFESSIONAL PRIVIP INSTALLER         ${NC}"
echo -e "${BLUE}==========================================${NC}"

echo -e "\n${YELLOW}[1/5] Checking system dependencies...${NC}"
if command -v pacman >/dev/null 2>&1; then
  sudo pacman -Sy --needed --noconfirm \
    base-devel \
    libpcap \
    python \
    python-pip \
    tk \
    libcap
elif command -v apt >/dev/null 2>&1; then
  sudo apt update -y && sudo apt install -y \
    build-essential \
    libpcap-dev \
    python3-venv \
    python3-pip \
    python3-tk \
    libcap2-bin
elif command -v dnf >/dev/null 2>&1; then
  sudo dnf install -y \
    @development-tools \
    libpcap-devel \
    python3-pip \
    python3-tkinter \
    libcap
else
  echo -e "${RED}No supported package manager found (pacman/apt/dnf).${NC}"
  echo -e "${YELLOW}Install manually: a C toolchain, libpcap headers, python3 with venv/tk, and setcap.${NC}"
fi

echo -e "\n${YELLOW}[2/5] Compiling Core engine in C...${NC}"
if make; then
  echo -e "${GREEN}C engine compiled successfully.${NC}"
else
  echo -e "${RED}Compilation error. Check build tools.${NC}"
  exit 1
fi

echo -e "\n${YELLOW}[3/5] Configuring network permissions for the binary...${NC}"
if sudo setcap 'cap_net_raw,cap_net_admin+ep' bin/privipchanger; then
  echo -e "${GREEN}Permissions configured (cap_net_admin).${NC}"
else
  echo -e "${RED}Error configuring setcap.${NC}"
fi

echo -e "\n${YELLOW}[4/5] Setting up Python virtual environment...${NC}"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
echo -e "${BLUE}Installing Python libraries...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
chmod +x cprivip.sh

echo -e "\n${BLUE}==========================================${NC}"
echo -e "${GREEN}INSTALLATION COMPLETED SUCCESSFULLY${NC}"
echo -e "${BLUE}==========================================${NC}"
echo -e "\nTo launch the application:"
echo -e "  ${BLUE}source .venv/bin/activate${NC}"
echo -e "  ${BLUE}python src/dashboard.py${NC}\n"
