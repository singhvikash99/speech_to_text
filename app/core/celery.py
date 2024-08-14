from celery import Celery

app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["app.core.tasks"],
)

if __name__ == "__main__":
    app.start()
