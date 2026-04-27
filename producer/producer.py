import json, time, requests
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="kafka:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

PRODUCTS_URL = "https://fakestoreapi.com/products"
ORDERS_URL = "https://fakestoreapi.com/carts"


def send_products():
    products = requests.get(PRODUCTS_URL, timeout=20).json()
    ingest_ts = int(time.time())
    producer.send(
        "ecommerce-products",
        {
            "type": "products_batch",
            "ingest_ts": ingest_ts,
            "count": len(products),
            "data": products,
        },
    )
    print(f"Sending {len(products)} products at {ingest_ts}")


def send_orders():
    orders = requests.get(ORDERS_URL, timeout=20).json()
    ingest_ts = int(time.time())
    producer.send(
        "ecommerce-orders",
        {
            "type": "orders_batch",
            "ingest_ts": ingest_ts,
            "count": len(orders),
            "data": orders,
        },
    )
    print(f"Sending {len(orders)} orders at {ingest_ts}")


if __name__ == "__main__":
    print("------")
    send_products()
    send_orders()
    producer.flush()
    print("Sent products + orders batches to Kafka")
