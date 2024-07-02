#!/bin/bash
echo "ValidateService script ejecutado."

# Verifica que el archivo index.html esté accesible a través de HTTP
RESPONSE=$(curl -o /dev/null -s -w "%{http_code}\n" http://localhost/index.html)

if [ "$RESPONSE" -eq 200 ]; then
  echo "Validación exitosa: index.html está accesible. Respuesta HTTP: $RESPONSE"
  exit 0
else
  echo "Validación fallida: index.html no está accesible. Respuesta HTTP: $RESPONSE"
  exit 1
fi