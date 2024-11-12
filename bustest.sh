#!/bin/bash
API=

if [ "$1" = "bus" ]; then
	API="https://rest.citybus.gr/api/v1/el/112/stops/live/$2"
elif [ "$1" = "stops" ]; then
  API="https://rest.citybus.gr/api/v1/el/112/stops"
else
  API=$1
fi

BUS_TOKEN=$(cat bus_token.txt)

if [ -z "$BUS_TOKEN" ]; then
  echo "Getting new token..."
  TOKEN_ENDPOINT="https://patra.citybus.gr/el/stops"
  BUS_TOKEN=$(curl -s -X GET $TOKEN_ENDPOINT | grep -Po "const token = '\K[^']+" | sed "s/^'\(.*\)'$/\1/")
  echo $BUS_TOKEN > "bus_token.txt"
fi

echo "TOKEN: $BUS_TOKEN"
echo "API: $API"
echo

curl -i -X GET $API -H "Authorization: Bearer $BUS_TOKEN" -H "Content-Type: application/json"
echo

