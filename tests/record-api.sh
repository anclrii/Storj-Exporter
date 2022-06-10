#!/bin/bash

api_url='http://localhost:14007/api'

sno=`curl -s "$api_url/sno/"`
version=`echo $sno | jq -r '.version'`
first_sat=`echo $sno | jq -r '.satellites | first | .id'`
mock_path="tests/api_mock/v$version"

mkdir -p $mock_path
echo $sno                                   | jq > $mock_path/sno.json
curl -s "$api_url/sno/estimated-payout"         | jq > $mock_path/payout.json
curl -s "$api_url/sno/satellite/$first_sat"     | jq > $mock_path/satellite.json