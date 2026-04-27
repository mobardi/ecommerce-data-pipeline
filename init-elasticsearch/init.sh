#!/usr/bin/env bash
set -e

until curl -s http://elasticsearch:9200 >/dev/null; do
  echo "Waiting for Elasticsearch..."
  sleep 2
done

echo "Installing index templates..."
curl -s -X PUT "http://elasticsearch:9200/_index_template/ecommerce-products-template" \
  -H "Content-Type: application/json" \
  --data-binary @/templates/products-template.json >/dev/null

curl -s -X PUT "http://elasticsearch:9200/_index_template/ecommerce-orders-template" \
  -H "Content-Type: application/json" \
  --data-binary @/templates/orders-template.json >/dev/null

echo "Templates installed."
