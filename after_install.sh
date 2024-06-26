#!/bin/bash
echo "AfterInstall script executed."
# Verificar que el bucket y la ruta del archivo son correctos
aws s3 cp s3://s3-bucket-ajose-dev/index.html /var/www/html/index.html
chmod 644 /var/www/html/index.html
