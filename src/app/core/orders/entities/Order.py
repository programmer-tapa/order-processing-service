from src.app.core.origin.entities.base_class import BaseClass


class Order(BaseClass):
    id: str
    customer_name: str
    total_amount: float
    status: str
    created_at: str
    updated_at: str
