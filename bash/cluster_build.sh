#!/usr/bin/env bash
set -euo pipefail

# Resolve working directory
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." &>/dev/null && pwd)"

cd "$REPO_ROOT"
echo "[INFO] Working directory set to: $PWD"

# Enable DHCP on the VLAN
echo "[INFO] Enabling DHCP in the kubernetes-lab VLAN"
( cd tofu && tofu apply -auto-approve -var dhcp_enabled=true )

echo "[AUDIENCE PARTICIPATION] Please plug in your new Ubuntu machine."
sleep 2

# Network scan for visibility only
echo "[INFO] Discovering hosts on the kubernetes-lab VLAN"
nmap -sn 192.168.8.0/24 || echo "[WARN] nmap scan failed (non-fatal)"

# Prompt for the new node's IP address
read -p "[INPUT] Ubuntu machine IP address: " bootstrap_ip

# Run the Ansible cluster setup
echo "[INFO] Installing required Ansible collections and roles"
ansible-galaxy install -r requirements.yml --force

echo "[INFO] Running Ansible cluster playbook on ${bootstrap_ip}"
if ansible-playbook -i "${bootstrap_ip}," -u ubuntu playbooks/cluster.yml; then
  echo "[INFO] Cluster bootstrap completed successfully."
else
  echo "[ERROR] Ansible cluster bootstrap failed. Exiting." >&2
  exit 1
fi

# Disable DHCP after provisioning
echo "[INFO] Disabling DHCP again on the kubernetes-lab VLAN"
( cd tofu && tofu apply -auto-approve -var dhcp_enabled=false )

echo "[SUCCESS] Cluster setup completed and DHCP restored to normal state."