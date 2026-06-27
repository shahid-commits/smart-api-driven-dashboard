# Smart API-Driven Dashboard — main application

from fastapi import FastAPI, Request            # brings in the tools we need from FastAPI
from fastapi.templating import Jinja2Templates  # lets us render HTML files with Python data inside
from fastapi.staticfiles import StaticFiles     # lets us serve CSS and JS files directly
from pydantic import BaseModel                  # lets us define the shape of POST request data
from dotenv import load_dotenv                  # reads our .env file so os.getenv() can access the keys
from groq import Groq                           # the Groq AI client

import requests                                 # for calling the weather API
import os                                       # lets us read environment variables

load_dotenv()           

app = FastAPI()         # create the main FastAPI app instance

app.mount("/static", StaticFiles(directory="static"), name="static")    # tell FastAPI to serve static files from the static/ folder

templates = Jinja2Templates(directory="templates")          # tell FastAPI where our HTML templates live

client = Groq(api_key=os.getenv("GROQ_API_KEY"))            # connect to Groq AI using the key from .env

# converts a city name to latitude and longitude
def get_coordinates(city: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {"name": city, "count": 1}         # city name goes as a query param

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # if no results found for this city name
        if not data.get("results"):
            return None
        
        # grab the first result's coordinates
        location = data["results"][0]
        return {
            "lat"       : location["latitude"],
            "lon"       : location["longitude"],
            "name"      : location["name"],
            "country"   : location["country"]
        }
    
    except Exception as e:
        print(f"Geocoding failed: {e}")
        return None
    
# fetches live weather data using coordinates
def get_weather(city: str):

    coords = get_coordinates(city)      # first convert city name to coordinates

    # if city not found return a clear error message
    if not coords:
        return {
            "city": city,
            "country": "",
            "temperature": "--",
            "humidity": "--",
            "windspeed": "--",
            "weathercode": 0,
            "error": f"City {city} not found"
        }
    
    url = "https://api.open-meteo.com/v1/forecast"

    # tell Open-Meteo exactly which fields we want back
    params = {
        "latitude"  : coords["lat"],
        "longitude" : coords["lon"],
        "current"   : "temperature_2m,weathercode,relativehumidity_2m,windspeed_10m",
        "timezone"  : "auto"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # pull out just the current weather block
        current = data["current"]

        return {
            "city"          : coords["name"],
            "country"       : coords["country"],
            "temperature"   : current["temperature_2m"],
            "humidity"      : current["relativehumidity_2m"],
            "windspeed"     : current["windspeed_10m"],
            "weathercode"   : current["weathercode"],
            "error"         : None
        }
    
    except Exception as e:
        print(f"Weather fetch failed: {e}")

        # return fallback so the app never fully crashes
        return {
            "city"          : city,
            "country"       : "",
            "temperature"   : "--",
            "humidity"      : "--",
            "windspeed"     : "--",
            "weathercode"   : 0,
            "error"         : "Weather service unavailable"
        }
    
# defines the shape of data we expect in the POST /ask request
class AskRequest(BaseModel):
    city    : str
    question: str

# main dashboard route - renders the html page with weather data
@app.get("/")
def dashboard(request: Request, city:str = "Mumbai"):

    weather = get_weather(city)         # fetch live weather for the requested city

    # pass weather data + request into the HTML template
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "city"          : weather["city"],
            "country"       : weather["country"],
            "temperature"   : weather["temperature"],
            "humidity"      : weather["humidity"],
            "windspeed"     : weather["windspeed"],
            "weathercode"   : weather["weathercode"],
            "error"         : weather["error"]
        }
    )

# AI route - receives a question and returns an AI answer
@app.post("/ask")
def ask(req: AskRequest):

    weather = get_weather(req.city)         # fetch fresh weather for the city in the request

    # build the prompt by injecting live weather + user question
    prompt = f"""
You are a helpful weather assistant embedded in a dashboard app.

Current weather data for {weather['city']}, {weather['country']}:
- Temperature   : {weather['temperature']}°C
- Humidity      : {weather['humidity']}%
- Wind Speed    : {weather['windspeed']} km/h

User question: {req.question}

Reply in one friendly sentence. No bullet points. No raw numbers.
"""
    
    # send the prompt to Groq and get the AI response
    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content        # extract just the text from the response

    return {"answer": answer, "weather": weather}