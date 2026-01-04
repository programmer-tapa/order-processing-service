import asyncio
import sys
import os

# Add the project root to python path
sys.path.append(os.getcwd())

from src.app.core.orders.features.processOrder.services.SERVICE_ProcessOrder import SERVICE_ProcessOrder
from src.app.core.orders.features.processOrder.schemas.INPUT_ProcessOrder import INPUT_ProcessOrder

async def main():
    try:
        req = INPUT_ProcessOrder(order_id=1)
        res = await SERVICE_ProcessOrder(req)
        print("Successfully processed order:")
        for order in res.processed_orders:
            print(f"Order ID: {order.id}, Customer: {order.customer_name}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
