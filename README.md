# Order Processing Service

A Python-based microservice for processing orders and handling Kafka events using a clean architecture pattern with use cases, interfaces, and contracts.

## Features

- **Order Processing** – Process incoming orders from Kafka events
- **Event-Driven Architecture** – Kafka consumer with Dead Letter Queue (DLQ) support
- **Dynamic Event Processors** – Automatically loads event processors based on event names
- **Clean Architecture** – Separation of concerns with use cases, interfaces, and contracts
- **Configurable Middleware** – CORS, GZip, TrustedHost, and HTTPS redirect support

## Project Structure

```
src/
├── app/
│   ├── core/                              # Business logic
│   │   ├── origin/                        # Shared base classes
│   │   │   └── entities/
│   │   │       ├── abstract_usecase.py
│   │   │       ├── abstract_factory.py
│   │   │       └── base_class.py
│   │   └── orders/                        # Orders domain
│   │       ├── entities/
│   │       │   └── Order.py
│   │       └── features/
│   │           └── processOrder/
│   │               ├── contracts/         # Concrete implementations
│   │               ├── interfaces/        # Abstract interfaces
│   │               ├── schemas/           # Input/Output DTOs
│   │               ├── services/          # Service orchestrators
│   │               └── usecases/          # Business use cases
│   └── infra/                             # Infrastructure layer
│       ├── dotenv/                        # Environment configuration
│       ├── logger/                        # Logging service
│       ├── events/
│       │   ├── entities/
│       │   │   ├── Event.py
│       │   │   ├── abstract_event_processor.py
│       │   │   └── concrete/              # Event processors (e.g., OrderCreated)
│       │   └── features/
│       │       └── process_events/        # Event processing feature
│       └── message_broker/
│           ├── contracts/                 # Kafka consumer adapter
│           ├── entities/                  # Abstract consumer adapter
│           ├── functions/                 # Start/stop consumer functions
│           ├── interfaces/                # Consumer interface
│           └── services/                  # Message broker service
└── framework/                             # Framework entrypoints
    └── entrypoints/
        ├── server.py                      # FastAPI app with Kafka lifecycle
        └── api/
            └── routes.py                  # API router
```

## Tech Stack

- **Python 3.12+**
- **FastAPI** – Web framework
- **Pydantic** – Data validation
- **Confluent Kafka** – Kafka consumer/producer
- **pytest** – Testing
- **uv** – Package manager

## Installation

```bash
# Install dependencies using uv
uv sync
```

## Configuration

Copy `.env.example` to `.env` and configure the following variables:

### Application Settings

| Variable         | Description           | Default                    |
| ---------------- | --------------------- | -------------------------- |
| `PRODUCTION_ENV` | Production mode flag  | `False`                    |
| `APP_NAME`       | Application name      | `Order Processing Service` |
| `APP_HOST`       | Server host           | `127.0.0.1`                |
| `APP_PORT`       | Server port           | `8000`                     |
| `APP_RELOAD`     | Hot reload (dev only) | `True`                     |

### Kafka Settings

| Variable                  | Description             | Default                  |
| ------------------------- | ----------------------- | ------------------------ |
| `KAFKA_BROKER_URL`        | Kafka broker address    | `localhost:9092`         |
| `KAFKA_GROUP_ID`          | Consumer group ID       | `order-processing-group` |
| `KAFKA_TOPIC`             | Topics to consume       | `["order-events"]`       |
| `KAFKA_DLQ_TOPIC`         | Dead Letter Queue topic | `orders-dlq`             |
| `KAFKA_AUTO_OFFSET_RESET` | Offset reset strategy   | `earliest`               |

### Middleware Settings

| Variable                       | Description             | Default |
| ------------------------------ | ----------------------- | ------- |
| `APP_MIDDLEWARE_CORS`          | Enable CORS middleware  | `True`  |
| `APP_MIDDLEWARE_GZIP`          | Enable GZip compression | `False` |
| `APP_MIDDLEWARE_TRUSTEDHOST`   | Enable trusted hosts    | `True`  |
| `APP_MIDDLEWARE_HTTPSREDIRECT` | Force HTTPS redirect    | `False` |

## Running the Service

### Development

```bash
uv run python main.py
```

### Production (Uvicorn)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production (Gunicorn + Uvicorn)

```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Running Tests

```bash
uv run pytest tests/ -v
```

## Architecture

This service follows a **Clean Architecture** pattern:

| Layer          | Description                                                        |
| -------------- | ------------------------------------------------------------------ |
| **Entities**   | Domain models (e.g., `Order`, `Event`)                             |
| **Use Cases**  | Business logic (e.g., `USECASE_ProcessOrder`)                      |
| **Interfaces** | Abstract contracts (e.g., `INTERFACE_HELPER_ProcessOrder`)         |
| **Contracts**  | Concrete implementations (e.g., `CONTRACT_HELPER_ProcessOrder_V0`) |
| **Services**   | Orchestrators that wire use cases with helpers                     |

## Event Processing Flow

```
┌─────────────────┐     ┌────────────────────────┐     ┌──────────────────────────────┐
│  Kafka Topic    │────▶│  KafkaConsumerAdapter  │────▶│  SERVICE_ProcessEvents       │
│  (order-events) │     │  (poll_messages)       │     │  (USECASE_ProcessEvents)     │
└─────────────────┘     └────────────────────────┘     └──────────────────────────────┘
                                   │                               │
                                   │ on error                      │ detect_event_processor
                                   ▼                               ▼
                        ┌─────────────────┐           ┌──────────────────────────────┐
                        │  DLQ Topic      │           │  EventProcessor_<EventName>  │
                        │  (orders-dlq)   │           │  (e.g., EventProcessor_      │
                        └─────────────────┘           │   OrderCreated)              │
                                                      └──────────────────────────────┘
```

1. **Kafka Consumer** polls messages from configured topics
2. **SERVICE_ProcessEvents** processes each event through the use case
3. **detect_event_processor** dynamically loads the appropriate processor based on event name
4. Failed messages are sent to the **Dead Letter Queue (DLQ)**

## Adding New Event Processors

1. Create a new file in `src/app/infra/events/entities/concrete/` named after the event (e.g., `OrderShipped.py`)
2. Implement the `EventProcessor_<EventName>` class:

```python
from src.app.infra.events.entities.abstract_event_processor import AbstractEventProcessor
from src.app.infra.events.entities.event import Event

class EventProcessor_OrderShipped(AbstractEventProcessor):

    async def process(self, event: Event) -> None:
        # Your processing logic here
        order_id = event.data.get("orderId")
        print(f"Processing OrderShipped event for order ID: {order_id}")
```

## Naming Conventions

| Type            | Pattern                                        | Example                           |
| --------------- | ---------------------------------------------- | --------------------------------- |
| Use Case        | `USECASE_<FeatureName>`                        | `USECASE_ProcessOrder`            |
| Interface       | `INTERFACE_HELPER_<FeatureName>`               | `INTERFACE_HELPER_ProcessOrder`   |
| Contract        | `CONTRACT_HELPER_<FeatureName>_V<N>`           | `CONTRACT_HELPER_ProcessOrder_V0` |
| Schema          | `INPUT_<FeatureName>` / `OUTPUT_<FeatureName>` | `INPUT_ProcessOrder`              |
| Service         | `SERVICE_<FeatureName>`                        | `SERVICE_ProcessOrder`            |
| Event Processor | `EventProcessor_<EventName>`                   | `EventProcessor_OrderCreated`     |

## License

MIT
