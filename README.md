# Bus Finder Project

This project includes:

- **Backend API**: FastAPI with SQLite database for user authentication, bus routes, and bookings.
- **Frontend**: Streamlit app that interacts with the backend API for searching and booking buses.

## How to Run

### Backend

1. Go to the backend directory:
    ```
    cd backend
    ```

2. Install requirements:
    ```
    pip install -r requirements.txt
    ```

3. Run the FastAPI server:
    ```
    uvicorn app:app --reload
    ```

### Frontend

1. Open a new terminal and go to the frontend directory:
    ```
    cd frontend
    ```

2. Install requirements:
    ```
    pip install -r requirements.txt
    ```

3. Run the Streamlit app:
    ```
    streamlit run streamlit_bus_app.py
    ```

### Usage

- Register a new user or login.
- Search buses between Indian cities.
- Book a bus for a date.
- View and cancel your bookings.