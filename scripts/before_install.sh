#!/bin/bash
echo "BeforeInstall script executed."
sudo apt-get update -y
sudo apt-get install -y apache2

if [ -f /var/www/html/index.py ]; then
  sudo rm /var/www/html/index.py
fi
if [ -f /var/www/html/ConsultaApi.py ]; then
  sudo rm /var/www/html/ConsultaApi.py
fi
if [ -f /var/www/html/ConsultaApi.py ]; then
  sudo rm /var/www/html/ConsultaApi.py
fi