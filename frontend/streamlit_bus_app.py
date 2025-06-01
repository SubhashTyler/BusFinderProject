import streamlit as st
import requests
import pandas as pd

API_BASE_URL = https://busfinderproject-1.onrender.com

def register(username, password):
    response = requests.post(f"{API_URL}/register", json={"username": username, "password": password})
    return response

def login(username, password):
    response = requests.post(f"{API_URL}/login", json={"username": username, "password": password})
    return response

def get_routes():
    response = requests.get(f"{API_URL}/routes")
    if response.ok:
        return response.json()
    return []

def search_buses(from_city, to_city):
    params = {"from_city": from_city, "to_city": to_city}
    response = requests.get(f"{API_URL}/search", params=params)
    if response.ok:
        return response.json()
    return []

def add_booking(username, from_city, to_city, bus, date):
    payload = {
        "username": username,
        "from_city": from_city,
        "to_city": to_city,
        "bus": bus,
        "date": date
    }
    response = requests.post(f"{API_URL}/bookings", json=payload)
    return response

def get_bookings(username):
    response = requests.get(f"{API_URL}/bookings/{username}")
    if response.ok:
        return response.json()
    return []

def delete_booking(booking_id):
    response = requests.delete(f"{API_URL}/bookings/{booking_id}")
    return response

st.title("🚌 Indian Bus Finder App")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.subheader("Login or Register")

    option = st.radio("Select", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Submit"):
        if option == "Register":
            res = register(username, password)
            if res.ok:
                st.success("Registration successful! Please login.")
            else:
                st.error(f"Error: {res.json().get('detail', 'Unknown error')}")
        else:
            res = login(username, password)
            if res.ok:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
            else:
                st.error(f"Error: {res.json().get('detail', 'Login failed')}")

else:
    st.sidebar.title(f"Hello, {st.session_state.username}!")
    menu = st.sidebar.selectbox("Menu", ["Home", "Search Bus", "My Bookings", "Logout"])

    if menu == "Home":
        st.header("Welcome to Indian Bus Finder")
        st.write("Use the sidebar to navigate the app.")

    elif menu == "Search Bus":
        st.header("Search Bus")
        from_city = st.selectbox("From City", ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata"])
        to_city = st.selectbox("To City", ["Pune", "Agra", "Mysore", "Tirupati", "Vijayawada", "Durgapur"])
        date = st.date_input("Select Date")
        if st.button("Search"):
            results = search_buses(from_city, to_city)
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df[["bus", "departure", "arrival"]])
                selected_bus = st.selectbox("Select Bus to Book", df["bus"])
                if st.button("Book Bus"):
                    res = add_booking(st.session_state.username, from_city, to_city, selected_bus, str(date))
                    if res.ok:
                        st.success("Booking Confirmed!")
                    else:
                        st.error("Booking Failed!")
            else:
                st.info("No buses found for this route.")

    elif menu == "My Bookings":
        st.header("My Bookings")
        bookings = get_bookings(st.session_state.username)
        if bookings:
            for b in bookings:
                st.write(f"Bus: {b['bus']}, From: {b['from_city']}, To: {b['to_city']}, Date: {b['date']}")
                if st.button(f"Cancel Booking {b['id']}"):
                    res = delete_booking(b['id'])
                    if res.ok:
                        st.success("Booking cancelled.")
                        st.experimental_rerun()
                    else:
                        st.error("Failed to cancel booking.")
        else:
            st.info("No bookings found.")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()
