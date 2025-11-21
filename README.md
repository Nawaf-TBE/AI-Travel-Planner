# AI Travel Planner

A Streamlit-based AI application that generates personalized travel plans using OpenAI and SerpAPI.  
The app provides flights, attractions, hotels, restaurants, and a complete itinerary based on user preferences.

## Features
- Fetches real-time flight options using SerpAPI  
- Generates activity recommendations using AI agents  
- Suggests hotels and restaurants  
- Creates a structured, day-by-day itinerary  
- User-friendly Streamlit interface  

## Requirements
Install project dependencies:

pip install -r requirements.txt


## Environment Variables
Create a `.env` file in the project root:

OPENAI_API_KEY=your_openai_key
SERPAPI_KEY=your_serpapi_key


Do not commit your `.env` file.

## Running the App
Start the Streamlit application:

streamlit run travelagent.py


The app will open in your browser at:

http://localhost:8501
