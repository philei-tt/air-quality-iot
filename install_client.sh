#!/bin/bash
set -ex  # Print each command and exit on error

# Check if the script is run as root.
if [[ $EUID -ne 0 ]]; then
  echo "This script must be run with sudo or as root."
  exit 1
fi

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
ABS_PYTHON_SCRIPT="$(realpath "${SCRIPT_DIR}/aqs_client_sensor.py")"
SERVICE_SRC="${SCRIPT_DIR}/services/aqs_client_sensor.service"
TMP_SERVICE="/tmp/aqs_client_sensor.service"
SERVICE_DEST="/etc/systemd/system/aqs_client_sensor.service"

# Replace "python3 aqs_client_sensor.py" with the absolute path.
sed "s|python3 aqs_client_sensor.py|/usr/bin/python3 ${ABS_PYTHON_SCRIPT}|g" "${SERVICE_SRC}" > "${TMP_SERVICE}"

sudo cp "${TMP_SERVICE}" "${SERVICE_DEST}"

sudo systemctl daemon-reload
sudo systemctl enable aqs_client_sensor.service
sudo systemctl start aqs_client_sensor.service
echo "Service aqs_client_sensor.service installed, enabled, and started successfully."