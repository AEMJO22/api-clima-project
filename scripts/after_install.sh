#!/bin/bash
echo "AfterInstall script executed."

# Copia el archivo index.html al directorio de Apache
sudo cp /index.html /var/www/html/

# Verifica que el archivo se haya copiado
if [ -f /var/www/html/index.html ]; then
  echo "Archivo index.html copiado correctamente."
else
  echo "Error: El archivo index.html no se pudo copiar."
fi

# Ajusta los permisos del archivo para asegurarte de que es accesible
sudo chmod 644 /var/www/html/index.html

# Reinicia Apache para asegurarte de que los cambios se apliquen
sudo systemctl restart apache2