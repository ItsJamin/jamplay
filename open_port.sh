#!/bin/bash

# Extract local subnet from default route (IPv4 only)
SUBNET=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}/\d+' | grep -v '127.0.0.1' | head -n1)

PORT=5050
PROTOCOL=tcp

echo "Detected local subnet: $SUBNET"
echo "Opening port $PORT for $SUBNET..."

if command -v ufw >/dev/null 2>&1 && sudo ufw status | grep -q "Status: active"; then
    echo "ufw is active, adding rule..."
    sudo ufw allow from $SUBNET to any port $PORT proto $PROTOCOL
    echo "✅ Port $PORT opened in ufw for $SUBNET"
else
    echo "ufw not active, falling back to iptables..."
    sudo iptables -A INPUT -p $PROTOCOL --dport $PORT -s ${SUBNET%/*} -j ACCEPT
    echo "✅ Port $PORT opened in iptables for $SUBNET"
    echo "⚠️ Warning: iptables rules might not persist after reboot!"
fi
