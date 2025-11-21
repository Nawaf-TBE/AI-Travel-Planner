import streamlit as st
import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# AGNO IMPORTS
from agno.agent import Agent
from agno.tools.serpapi import SerpApiTools
from agno.models.openai import OpenAIChat

# -------------------------------------------------------
# STREAMLIT UI SETUP
# -------------------------------------------------------
st.set_page_config(page_title="🌍 AI Travel Planner", layout="wide")
st.markdown(
    """
    <style>
        .title {
            text-align: center;
            font-size: 36px;
            font-weight: bold;
            color: #ff5733;
        }
        .subtitle {
            text-align: center;
            font-size: 20px;
            color: #555;
        }
        .stSlider > div {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="title">✈️ AI-Powered Travel Planner</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Plan your dream trip with AI! Get personalized recommendations for flights, hotels, and activities.</p>', unsafe_allow_html=True)

# -------------------------------------------------------
# ENVIRONMENT VARIABLES
# -------------------------------------------------------
load_dotenv()

# Ensure keys exist
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SERPAPI_KEY:
    st.error("⚠️ SERPAPI_KEY is missing. Please add it to your .env file.")
    st.stop()

if not OPENAI_API_KEY:
    st.error("⚠️ OPENAI_API_KEY is missing. Please add it to your .env file.")
    st.stop()

# Set the OpenAI key for the environment
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# -------------------------------------------------------
# USER INPUTS
# -------------------------------------------------------
st.markdown("### 🌍 Where are you headed?")
col1, col2 = st.columns(2)
with col1:
    source = st.text_input("🛫 Departure City (IATA Code):", "BOM")
with col2:
    destination = st.text_input("🛬 Destination (IATA Code):", "DEL")

st.markdown("### 📅 Plan Your Adventure")
num_days = st.slider("🕒 Trip Duration (days):", 1, 14, 5)

col3, col4 = st.columns(2)
with col3:
    departure_date = st.date_input("Departure Date", datetime.today())
with col4:
    return_date = st.date_input("Return Date", datetime.today())

travel_theme = st.selectbox(
    "🎭 Select Your Travel Theme:",
    ["💑 Couple Getaway", "👨‍👩‍👧‍👦 Family Vacation", "🏔️ Adventure Trip", "🧳 Solo Exploration"]
)

activity_preferences = st.text_area(
    "🌍 What activities do you enjoy?",
    "Relaxing on the beach, exploring historical sites"
)

st.markdown("---")

# Sidebar Setup
st.sidebar.title("🌎 Travel Assistant")
st.sidebar.subheader("Personalize Your Trip")

budget = st.sidebar.radio("💰 Budget Preference:", ["Economy", "Standard", "Luxury"])
flight_class = st.sidebar.radio("✈️ Flight Class:", ["Economy", "Business", "First Class"])
hotel_rating = st.sidebar.selectbox("🏨 Preferred Hotel Rating:", ["Any", "3⭐", "4⭐", "5⭐"])

# Packing Checklist
st.sidebar.subheader("🎒 Packing Checklist")
packing_list = {
    "👕 Clothes": True,
    "🩴 Comfortable Footwear": True,
    "🕶️ Sunglasses & Sunscreen": False,
    "📖 Travel Guidebook": False,
    "💊 Medications & First-Aid": True
}
for item, checked in packing_list.items():
    st.sidebar.checkbox(item, value=checked)

st.sidebar.subheader("🛂 Travel Essentials")
visa_required = st.sidebar.checkbox("🛃 Check Visa Requirements")
travel_insurance = st.sidebar.checkbox("🛡️ Get Travel Insurance")
currency_converter = st.sidebar.checkbox("💱 Currency Exchange Rates")

# -------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------
def fetch_flights(source, destination, departure_date, return_date):
    params = {
        "engine": "google_flights",
        "departure_id": source,
        "arrival_id": destination,
        "outbound_date": str(departure_date),
        "return_date": str(return_date),
        "currency": "INR",
        "hl": "en",
        "api_key": SERPAPI_KEY
    }
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error fetching flight data: {response.status_code}")
            return {}
    except Exception as e:
        st.error(f"An error occurred while fetching flights: {e}")
        return {}

def extract_cheapest_flights(flight_data):
    best_flights = flight_data.get("best_flights", [])
    if not best_flights:
        return []
    # Sort by price if available, otherwise handle gracefully
    sorted_flights = sorted(best_flights, key=lambda x: x.get("price", float("inf")))[:3]
    return sorted_flights

# -------------------------------------------------------
# AGENTS
# -------------------------------------------------------

# Researcher Agent
researcher = Agent(
    name="Researcher",
    instructions=[
        "Identify the travel destination specified by the user.",
        "Gather detailed information on the destination, including climate, culture, and safety tips.",
        "Find popular attractions, landmarks, and must-visit places.",
        "Search for activities that match the user’s interests and travel style.",
        "Provide structured summaries with key insights."
    ],
    model=OpenAIChat(id="gpt-4o"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

# Planner Agent 
planner = Agent(
    name="Planner",
    instructions=[
        "Create a detailed day-by-day itinerary.",
        "Optimize schedule based on user budget and preferences.",
        "Estimate travel times and activity durations.",
        "Provide a well-formatted final itinerary."
    ],
    model=OpenAIChat(id="gpt-4o"),
)

# Hotels & Restaurants Agent
hotel_restaurant_finder = Agent(
    name="Hotel & Restaurant Finder",
    instructions=[
        "Search for top-rated hotels near major attractions.",
        "Recommend restaurants matching user preferences.",
        "Prioritize based on ratings, price, and distance."
    ],
    model=OpenAIChat(id="gpt-4o"),
    tools=[SerpApiTools(api_key=SERPAPI_KEY)],
)

# -------------------------------------------------------
# MAIN LOGIC
# -------------------------------------------------------

st.markdown(
    f"""
    <div style="
        text-align: center; 
        padding: 15px; 
        background-color: #ffecd1; 
        border-radius: 10px; 
        margin-top: 20px;
    ">
        <h3>🌟 Your {travel_theme} to {destination} is about to begin! 🌟</h3>
        <p>Let's find the best flights, stays, and experiences for your unforgettable journey.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("🚀 Generate Travel Plan"):
    
    # 1. Fetch Flights
    with st.spinner("✈️ Fetching flights..."):
        flight_data = fetch_flights(source, destination, departure_date, return_date)
        cheapest_flights = extract_cheapest_flights(flight_data)

    # 2. Research Attractions
    with st.spinner("🔍 Researching attractions..."):
        research_prompt = (
            f"Research the best attractions and activities in {destination} "
            f"for a {num_days}-day {travel_theme.lower()} trip. "
            f"The traveler enjoys: {activity_preferences}. Budget: {budget}."
        )
        research_results = researcher.run(research_prompt, stream=False)

    # 3. Find Hotels & Restaurants
    with st.spinner("🏨 Finding hotels & restaurants..."):
        hotel_prompt = (
            f"Find the best hotels and restaurants near attractions in {destination}. "
            f"Preferences: {activity_preferences}, Budget: {budget}, Hotel Rating: {hotel_rating}."
        )
        hotel_restaurant_results = hotel_restaurant_finder.run(hotel_prompt, stream=False)

    # 4. Create Itinerary
    with st.spinner("🗺️ Creating itinerary..."):
        planning_prompt = (
            f"Create a {num_days}-day itinerary for {destination}. "
            f"Attractions: {research_results.content}. "
            f"Hotels: {hotel_restaurant_results.content}. "
            f"Flight options: {json.dumps(cheapest_flights)}."
        )
        itinerary = planner.run(planning_prompt, stream=False)

    # -------------------------------------------------------
    # DISPLAY RESULTS
    # -------------------------------------------------------
    st.markdown("---")
    
    st.subheader("✈️ Flight Options")
    if cheapest_flights:
        st.json(cheapest_flights)
    else:
        st.warning("No specific flight details found for these dates.")

    st.subheader("🏨 Hotels & Dining")
    st.write(hotel_restaurant_results.content)

    st.subheader("🗺️ Your Itinerary")
    st.write(itinerary.content)

    st.success("✅ Travel plan generated successfully!")