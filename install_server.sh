#!/bin/bash
set -ex  # Print each command and exit on error

# Check if the script is run as root.
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run with sudo or as root."
  exit 1
fi

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
ABS_PYTHON_SCRIPT="$(realpath "${SCRIPT_DIR}/aqs_server_actuator.py")"
SERVICE_SRC="${SCRIPT_DIR}/services/aqs_server_actuator.service"
TMP_SERVICE="/tmp/aqs_server_actuator.service"
SERVICE_DEST="/etc/systemd/system/aqs_server_actuator.service"

# Replace "python3 aqs_server_actuator.py" with the absolute path.
sed "s|python3 aqs_server_actuator.py|/usr/bin/python3 ${ABS_PYTHON_SCRIPT}|g" "${SERVICE_SRC}" > "${TMP_SERVICE}"

sudo cp "${TMP_SERVICE}" "${SERVICE_DEST}"

sudo systemctl daemon-reload
sudo systemctl enable aqs_server_actuator.service
sudo systemctl start aqs_server_actuator.service
echo "Service aqs_server_actuator.service installed, enabled, and started successfully."