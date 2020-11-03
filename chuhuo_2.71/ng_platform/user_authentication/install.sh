#!/bin/sh

if [ ! -d "/usr/bin/userauth" ];then
mkdir -p /usr/bin/userauth
else
rm -rf /usr/bin/userauth/* 
fi

gcc portal_client.c -o portal_client
gcc user_attestation.c -o user_attestation -lpython2.7

chmod +x start_auth_server.sh
chmod +x set_auth_iptables.sh
chmod +x clean_iptables.sh

\cp portal_client user_attestation start_auth_server.sh set_auth_iptables.sh clean_iptables.sh /usr/bin/userauth
