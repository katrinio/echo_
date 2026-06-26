import uvicorn


def run() -> None:
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000)


def run_dev() -> None:
    import os
    os.environ["DATABASE_URL"] = "sqlite:///echo_dev.db"
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000, reload=True)
