#!/bin/bash
echo "ValidateService script executed."
sleep 10
response=$(curl --write-out "%{http_code}" --silent --output /dev/null http://localhost/index.html)

if [ "$response" -eq 200 ]; then
  echo "Validación exitosa: index.html está accesible."
  exit 0
else
  echo "Validación fallida: index.html no está accesible. Respuesta HTTP: $response"
  exit 1
fi
