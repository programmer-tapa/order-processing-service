# Order Processing Service

A Python-based microservice for processing orders using a clean architecture pattern with use cases, interfaces, and contracts.

## Project Structure

```
src/
├── app/
│   ├── core/                          # Business logic
│   │   ├── origin/                    # Shared base classes
│   │   │   └── entities/
│   │   │       ├── abstract_usecase.py
│   │   │       ├── abstract_factory.py
│   │   │       └── base_class.py
│   │   └── orders/                    # Orders domain
│   │       ├── entities/
│   │       │   └── Order.py
│   │       └── features/
│   │           └── processOrder/
│   │               ├── contracts/     # Concrete implementations
│   │               ├── interfaces/    # Abstract interfaces
│   │               ├── schemas/       # Input/Output DTOs
│   │               ├── services/      # Service orchestrators
│   │               └── usecases/      # Business use cases
│   └── infra/                         # Infrastructure layer
│       ├── events/
│       │   └── entities/
│       │       └── Event.py
│       └── event_processors/
│           └── features/
│               └── process_events/
└── framework/                         # Framework entrypoints
    └── entrypoints/
        └── server.py
```

## Tech Stack

- **Python 3.12+**
- **FastAPI** – Web framework
- **Pydantic** – Data validation
- **pytest** – Testing

## Installation

```bash
# Install dependencies using uv
uv sync
```

## Running the Service

```bash
uv run python main.py
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

## Naming Conventions

| Type      | Pattern                                        | Example                           |
| --------- | ---------------------------------------------- | --------------------------------- |
| Use Case  | `USECASE_<FeatureName>`                        | `USECASE_ProcessOrder`            |
| Interface | `INTERFACE_HELPER_<FeatureName>`               | `INTERFACE_HELPER_ProcessOrder`   |
| Contract  | `CONTRACT_HELPER_<FeatureName>_V<N>`           | `CONTRACT_HELPER_ProcessOrder_V0` |
| Schema    | `INPUT_<FeatureName>` / `OUTPUT_<FeatureName>` | `INPUT_ProcessOrder`              |
| Service   | `SERVICE_<FeatureName>`                        | `SERVICE_ProcessOrder`            |
