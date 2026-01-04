"""
To run server with Uvicorn with workers ( sample command ) :

    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

To run server with Gunicorn + Uvicorn ( sample command ) :

    gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

"""

from src.framework.entrypoints.server import app

"""
To start a dev server, set the necessary variables in .env and directly use the command :

    python3 main.py

"""
if __name__ == "__main__":
    import uvicorn
    from src.app.infra.dotenv.services.service_dotenv import (
        get_service_dotenv,
    )

    dotenv = get_service_dotenv()
    uvicorn.run(
        "main:app",
        host=dotenv.APP_HOST,
        port=dotenv.APP_PORT,
        reload=dotenv.APP_RELOAD,  # reload should be False in production
    )
