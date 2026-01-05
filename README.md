# Order Processing Service

A Python-based microservice for processing orders and handling Kafka events using a clean architecture pattern with use cases, interfaces, and contracts.

## Features

- **Order Processing** – Process incoming orders from Kafka events with validation, shipping calculation, discounts, and customer notifications
- **Order Cancellation** – Cancel orders with refund calculation and customer notifications
- **Event-Driven Architecture** – Kafka consumer with Dead Letter Queue (DLQ) support
- **Dynamic Event Processors** – Automatically loads event processors based on event names
- **Clean Architecture** – Separation of concerns with use cases, interfaces, and contracts
- **Centralized Logging** – Abstract logger service with colored console output and file logging
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
│   │   ├── orders/                        # Orders domain
│   │   │   ├── entities/
│   │   │   │   └── Order.py
│   │   │   └── features/
│   │   │       └── processOrder/
│   │   │           ├── contracts/         # Concrete implementations
│   │   │           ├── exceptions/        # Feature-specific exceptions
│   │   │           ├── factory/           # Entry point / DI
│   │   │           ├── interfaces/        # Abstract interfaces
│   │   │           ├── schemas/           # Input/Output DTOs
│   │   │           ├── services/          # Service orchestrators
│   │   │           └── usecases/          # Business use cases
│   │   │       └── cancelOrder/           # Same structure as processOrder
│   │   │           ├── contracts/
│   │   │           ├── exceptions/
│   │   │           ├── factory/
│   │   │           ├── interfaces/
│   │   │           ├── schemas/
│   │   │           ├── services/
│   │   │           └── usecases/
│   │   └── system/                        # System-level utilities
│   └── infra/                             # Infrastructure layer
│       ├── dotenv/                        # Environment configuration
│       │   └── services/
│       ├── logger/                        # Logging service
│       │   ├── interfaces/                # LoggerService interface
│       │   ├── contracts/                 # LoggerServiceContractV0
│       │   └── services/                  # get_service_logger()
│       ├── events/
│       │   ├── entities/
│       │   │   ├── event.py
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
├── framework/                             # Framework entrypoints
│   ├── entrypoints/
│   │   ├── server.py                      # FastAPI app with Kafka lifecycle
│   │   └── api/
│   │       └── routes.py                  # API router
│   └── middlewares/                       # Custom middleware
│       ├── debugger.py
│       └── route_error_handler.py
└── tests/                                 # Test suite (mirrors src structure)
    └── app/
        └── core/
            └── orders/
                └── features/
                    ├── processOrder/
                    │   └── usecases/
                    │       └── test_USECASE_ProcessOrder.py
                    └── cancelOrder/
                        └── usecases/
                            └── test_USECASE_CancelOrder.py
```

## Tech Stack

- **Python 3.12+**
- **FastAPI** – Web framework
- **Pydantic** – Data validation
- **Confluent Kafka** – Kafka consumer/producer
- **pytest** – Testing with async support
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
| `API_V1_STR`     | API version prefix    | `/api/v0`                  |
| `OPENAPI_URL`    | OpenAPI docs URL      | `/apidocs`                 |
| `LOG_FILE`       | Error log file path   | `error.log`                |

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

### CORS Settings

| Variable                   | Description           | Default |
| -------------------------- | --------------------- | ------- |
| `BACKEND_CORS_ORIGINS`     | Allowed origins       | `["*"]` |
| `BACKEND_CORS_CREDENTIALS` | Allow credentials     | `True`  |
| `BACKEND_CORS_METHODS`     | Allowed HTTP methods  | `["*"]` |
| `BACKEND_CORS_HEADERS`     | Allowed headers       | `["*"]` |
| `BACKEND_ALLOWED_HOSTS`    | Trusted host patterns | `["*"]` |

## Running the Service

### Development

```bash
uv run python3 main.py
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
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/app/core/orders/features/processOrder/usecases/test_USECASE_ProcessOrder.py -v
```

## Architecture

### Architecture Philosophy

This codebase implements **Vertical Slice Architecture** combined with **Clean Architecture** principles, designed for **feature-driven development** in enterprise environments.

#### Why This Structure?

| Common First Impression          | Actual Intent                                                         |
| -------------------------------- | --------------------------------------------------------------------- |
| "Over-engineered"                | Deliberate vertical slice architecture for scalable team development  |
| "Too many files"                 | Proper separation of concerns – each file has a single responsibility |
| "Java patterns forced on Python" | Framework-agnostic patterns that work in any language                 |

#### Design Decisions

1. **Vertical Slices over Horizontal Layers**

   - Each feature (`processOrder`, `cancelOrder`) is a self-contained unit
   - Adding a new feature = adding a new folder, not modifying existing code
   - Deleting a feature = deleting a folder, with zero impact on other features

2. **Explicit Naming Convention**

   - `USECASE_`, `SERVICE_`, `CONTRACT_`, `INTERFACE_` prefixes make the role of each class immediately clear
   - Self-documenting code that scales across large teams
   - Enables quick navigation in large codebases

3. **Dependency Inversion**

   - Business logic (use cases) depends on abstractions (interfaces), not implementations
   - Contracts can be swapped without changing business logic (e.g., `V0` → `V1`)
   - Enables easy testing with mock implementations

4. **Factory Pattern for DI**
   - No framework dependency for dependency injection
   - Explicit wiring makes the dependency graph visible
   - Singleton pattern for performance-critical services

This architecture is particularly suited for:

- 🏢 **Enterprise microservices** with multiple teams
- 🔄 **Polyglot environments** (same patterns in Python, Java, TypeScript)
- 📈 **Rapidly evolving products** where features are added/removed frequently

---

### Clean Architecture Layers

| Layer          | Description                                                        |
| -------------- | ------------------------------------------------------------------ |
| **Entities**   | Domain models (e.g., `Order`, `Event`)                             |
| **Use Cases**  | Business logic (e.g., `USECASE_ProcessOrder`)                      |
| **Interfaces** | Abstract contracts (e.g., `INTERFACE_HELPER_ProcessOrder`)         |
| **Contracts**  | Concrete implementations (e.g., `CONTRACT_HELPER_ProcessOrder_V0`) |
| **Services**   | Orchestrators that wire use cases with helpers                     |
| **Factory**    | Entry points with DI and singleton pattern                         |

### Vertical Slice Architecture

Each feature is a **self-contained vertical slice** containing all layers:

```
features/
└── processOrder/           ← Vertical Slice (self-contained feature)
    ├── schemas/            ← Input/Output DTOs
    ├── interfaces/         ← Ports (abstractions)
    ├── contracts/          ← Adapters (implementations)
    ├── exceptions/         ← Feature-specific errors
    ├── usecases/           ← Business logic
    ├── services/           ← Orchestration
    └── factory/            ← Entry point / DI
```

**Benefits:**

- ✅ **Self-contained** – All layers within one folder
- ✅ **Independently deployable** – Clear boundaries
- ✅ **Easy to delete** – Remove folder = remove feature
- ✅ **Parallel development** – Teams can work on different features

### Order Processing Workflow

The `USECASE_ProcessOrder` executes the following steps:

1. **Load Order** – Retrieve order by ID from the data source
2. **Validate Order** – Ensure order is in a processable state (`new` or `pending`)
3. **Calculate Shipping** – Determine shipping cost (free for orders ≥ $100)
4. **Apply Discounts** – Apply percentage-based discounts (default 10%)
5. **Calculate Final Total** – `total_amount + shipping - discount`
6. **Update Order Status** – Set status to `processing`
7. **Notify Customer** – Send notification with order details

### Order Cancellation Workflow

The `USECASE_CancelOrder` executes the following steps:

1. **Load Order** – Retrieve order by ID from the data source
2. **Validate Cancellable** – Ensure order can be cancelled (`new`, `pending`, or `processing` status)
3. **Calculate Refund** – Determine refund amount (order total - 5% cancellation fee)
4. **Update Order Status** – Set status to `cancelled`
5. **Notify Customer** – Send cancellation notification with refund details

## Logging Service

The service uses a centralized logging infrastructure with:

- **Abstract Interface** – `LoggerService` with `debug`, `info`, `warning`, `error`, `critical` methods
- **Colored Console Output** – Different colors for each log level for better visibility
- **File Logging** – Errors are logged to the configured `LOG_FILE`
- **Singleton Pattern** – `get_service_logger()` returns a cached logger instance

### Usage

```python
from src.app.infra.logger.services.service_logger import get_service_logger

logger = get_service_logger()
logger.info("Processing order...")
logger.error("Failed to process order")
```

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
from src.app.infra.logger.services.service_logger import get_service_logger

class EventProcessor_OrderShipped(AbstractEventProcessor):
    def __init__(self):
        self._logger = get_service_logger()

    async def process(self, event: Event) -> None:
        order_id = event.data.get("orderId")
        self._logger.info(f"Processing OrderShipped event for order ID: {order_id}")
        # Your processing logic here
```

## Kafka Event Schema

Events consumed from Kafka follow this structure:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "OrderCreated",
  "data": {
    "orderId": "12345",
    "customerId": "cust-789",
    "totalAmount": 150.0,
    "currency": "INR",
    "status": "CREATED",
    "items": [
      {
        "productId": "prod-001",
        "quantity": 2,
        "unitPrice": 75.0,
        "totalPrice": 150.0
      }
    ],
    "createdAt": "2026-01-05T11:34:53.145Z"
  }
}
```

| Field              | Type   | Description                                       |
| ------------------ | ------ | ------------------------------------------------- |
| `id`               | UUID   | Unique event identifier                           |
| `name`             | string | Event type (e.g., `OrderCreated`, `OrderShipped`) |
| `data`             | object | Event-specific payload                            |
| `data.orderId`     | string | Order identifier                                  |
| `data.customerId`  | string | Customer identifier                               |
| `data.totalAmount` | float  | Order total                                       |
| `data.currency`    | string | Currency code (ISO 4217)                          |

## Failure Handling & Reliability

### Implemented Failsafe Mechanisms

| Mechanism                   | Implementation                                                  |
| --------------------------- | --------------------------------------------------------------- |
| **Connection Retry**        | 5 attempts with exponential backoff (1s → 2s → 4s → 8s → 16s)   |
| **Correlation IDs**         | UUID generated per message for distributed tracing `[abc12345]` |
| **Safe JSON Parsing**       | Invalid JSON caught and routed to DLQ                           |
| **Double-Close Prevention** | `_consumer_closed` flag prevents errors                         |
| **DLQ with Metadata**       | Headers include `correlation_id` and `error_reason`             |
| **Graceful Shutdown**       | Interruptible sleep, stop flag checked on each iteration        |
| **Poll Auto-Restart**       | While loop with 5s delay replaces recursive calls               |

### Error Handling Flow

```
Message Received
      │
      ▼
┌─────────────────┐    Invalid JSON    ┌─────────────┐
│  JSON Parsing   │ ─────────────────▶ │     DLQ     │
└────────┬────────┘                    │  (headers)  │
         │                             └─────────────┘
         │ Valid JSON                         ▲
         ▼                                    │
┌─────────────────┐    Processing      ───────┘
│ Event Processor │    Failed
└────────┬────────┘
         │
         │ Success
         ▼
   Message Logged
```

### Dead Letter Queue (DLQ)

Failed messages are routed to `orders-dlq` topic with:

- `correlation_id` header for tracing
- `error_reason` header (truncated to 500 chars)
- Original message key and value preserved

### Future Enhancements

| Enhancement           | Description                                     |
| --------------------- | ----------------------------------------------- |
| Health Check Endpoint | Kubernetes readiness probe integration          |
| Manual Offset Commit  | At-least-once delivery guarantee                |
| Circuit Breaker       | Prevent cascade failures to downstream services |
| Consumer Scaling      | Horizontal scaling via topic partitioning       |

## Interview Talking Points

<details>
<summary>Click to expand prepared answers for common interview questions</summary>

### "Describe the architecture"

> "This is a Python FastAPI service that consumes Kafka events and executes domain use cases. Domain logic is isolated from messaging and framework concerns using Clean Architecture with Vertical Slices. Infrastructure concerns are implemented via interfaces and concrete adapters."

### "Why Clean Architecture?"

> "It enables independent testing of business rules, isolates side-effects, and makes it easy to swap implementations (e.g., Kafka → RabbitMQ, Mock → PostgreSQL) without changing core logic. Each feature is a self-contained vertical slice that can be developed, tested, and deployed independently."

### "Explain DLQ & reliability"

> "Messages that fail processing get routed to a Dead Letter Queue. This ensures problematic messages are observable and debuggable without halting the pipeline. In production, I'd add retry logic with exponential backoff before DLQ routing."

### "How would you scale this?"

> "The consumer group design supports parallel processing. I'd partition topics based on order ID for ordering guarantees, scale consumers horizontally, and use Kubernetes HPA based on consumer lag metrics."

### "What happens if Kafka is down?"

> "On startup, the consumer would retry connection with backoff. I'd implement a health check that reports 'unhealthy' until Kafka is available. In production, I'd add circuit breaker patterns to prevent cascade failures."

</details>

## Naming Conventions

| Type            | Pattern                                        | Example                           |
| --------------- | ---------------------------------------------- | --------------------------------- |
| Use Case        | `USECASE_<FeatureName>`                        | `USECASE_ProcessOrder`            |
| Interface       | `INTERFACE_HELPER_<FeatureName>`               | `INTERFACE_HELPER_ProcessOrder`   |
| Contract        | `CONTRACT_HELPER_<FeatureName>_V<N>`           | `CONTRACT_HELPER_ProcessOrder_V0` |
| Schema          | `INPUT_<FeatureName>` / `OUTPUT_<FeatureName>` | `INPUT_ProcessOrder`              |
| Service         | `SERVICE_<FeatureName>`                        | `SERVICE_ProcessOrder`            |
| Event Processor | `EventProcessor_<EventName>`                   | `EventProcessor_OrderCreated`     |

> **Note:** These prefixes are intentional, not a deviation from PEP 8. They provide self-documenting code where the role of each class is immediately clear at a glance. This pattern is particularly valuable in polyglot environments where the same conventions work across Python, Java, and TypeScript codebases.

## API Documentation

When running in development mode (`PRODUCTION_ENV=False`), Swagger UI is available at:

- **Swagger UI**: `http://localhost:8000/docs`

## License

MIT
