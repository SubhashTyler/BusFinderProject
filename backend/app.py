from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import databases
import sqlalchemy
from passlib.context import CryptContext

DATABASE_URL = "sqlite:///./busfinder.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True),
    sqlalchemy.Column("hashed_password", sqlalchemy.String),
)

routes = sqlalchemy.Table(
    "routes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("from_city", sqlalchemy.String),
    sqlalchemy.Column("to_city", sqlalchemy.String),
    sqlalchemy.Column("bus", sqlalchemy.String),
    sqlalchemy.Column("departure", sqlalchemy.String),
    sqlalchemy.Column("arrival", sqlalchemy.String),
)

bookings = sqlalchemy.Table(
    "bookings",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("user_id", sqlalchemy.Integer),
    sqlalchemy.Column("from_city", sqlalchemy.String),
    sqlalchemy.Column("to_city", sqlalchemy.String),
    sqlalchemy.Column("bus", sqlalchemy.String),
    sqlalchemy.Column("date", sqlalchemy.String),
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

app = FastAPI()

# Schemas
class Route(BaseModel):
    id: int
    from_city: str
    to_city: str
    bus: str
    departure: str
    arrival: str

class BookingIn(BaseModel):
    username: str
    from_city: str
    to_city: str
    bus: str
    date: str

class BookingOut(BaseModel):
    id: int
    user_id: int
    from_city: str
    to_city: str
    bus: str
    date: str

    class Config:
        orm_mode = True

class UserIn(BaseModel):
    username: str
    password: str

# Utils
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Routes
@app.on_event("startup")
async def startup():
    await database.connect()
    query = routes.select()
    existing_routes = await database.fetch_all(query)
    if not existing_routes:
        sample_routes = [
            {"from_city": "Mumbai", "to_city": "Pune", "bus": "Shivneri Express", "departure": "07:00", "arrival": "10:00"},
            {"from_city": "Delhi", "to_city": "Agra", "bus": "Rajdhani Express", "departure": "09:00", "arrival": "12:00"},
            {"from_city": "Bangalore", "to_city": "Mysore", "bus": "Kaveri Deluxe", "departure": "06:30", "arrival": "09:30"},
            {"from_city": "Chennai", "to_city": "Tirupati", "bus": "Godavari Express", "departure": "08:00", "arrival": "11:00"},
            {"from_city": "Hyderabad", "to_city": "Vijayawada", "bus": "Deccan Queen", "departure": "13:00", "arrival": "17:00"},
            {"from_city": "Kolkata", "to_city": "Durgapur", "bus": "Eastern Star", "departure": "10:00", "arrival": "13:00"},
        ]
        for r in sample_routes:
            query = routes.insert().values(**r)
            await database.execute(query)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/register")
async def register(user: UserIn):
    query = users.select().where(users.c.username == user.username)
    existing = await database.fetch_one(query)
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    hashed = get_password_hash(user.password)
    query = users.insert().values(username=user.username, hashed_password=hashed)
    await database.execute(query)
    return {"message": "User registered successfully"}

@app.post("/login")
async def login(user: UserIn):
    query = users.select().where(users.c.username == user.username)
    db_user = await database.fetch_one(query)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"message": "Login successful"}

@app.get("/routes", response_model=List[Route])
async def get_routes():
    query = routes.select()
    return await database.fetch_all(query)

@app.get("/search")
async def search_buses(from_city: str, to_city: str):
    query = routes.select().where((routes.c.from_city == from_city) & (routes.c.to_city == to_city))
    return await database.fetch_all(query)

@app.post("/bookings")
async def add_booking(booking: BookingIn):
    query = users.select().where(users.c.username == booking.username)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    data = {
        "user_id": user["id"],
        "from_city": booking.from_city,
        "to_city": booking.to_city,
        "bus": booking.bus,
        "date": booking.date
    }
    query = bookings.insert().values(**data)
    await database.execute(query)
    return {"message": "Booking added"}

@app.get("/bookings/{username}", response_model=List[BookingOut])
async def get_user_bookings(username: str):
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    query = bookings.select().where(bookings.c.user_id == user["id"])
    records = await database.fetch_all(query)

    bookings_list = [
        {
            "id": record["id"],
            "user_id": record["user_id"],
            "from_city": record["from_city"],
            "to_city": record["to_city"],
            "bus": record["bus"],
            "date": record["date"],
        }
        for record in records
    ]
    return bookings_list

@app.delete("/bookings/{booking_id}")
async def delete_booking(booking_id: int):
    query = bookings.delete().where(bookings.c.id == booking_id)
    await database.execute(query)
    return {"message": "Booking deleted"}
