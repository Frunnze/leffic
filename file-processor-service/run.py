from app import create_app


app = create_app()

# To run the app with uvicorn
# uvicorn run:app --host 0.0.0.0 --port 80 --reload
# fastapi dev run.py