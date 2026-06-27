# Smart API-Driven Dashboard

A live weather dashboard built with FastAPI that fetches real-time weather data and answers user questions using Groq AI.

## Features
- Live weather for any city worldwide via Open-Meteo API
- AI-powered answers to weather questions using Groq (llama-3.3-70b)
- Clean dark dashboard built with Jinja2, CSS and JavaScript
- Error handling for invalid cities

## Tech Stack
- Python, FastAPI, Uvicorn
- Open-Meteo API (free, no key needed)
- Groq AI API
- Jinja2, HTML, CSS, JavaScript

## Setup
1. Clone the repo
2. Create a virtual environment and activate it
3. Run `pip install -r requirements.txt`
4. Create a `.env` file and add `GROQ_API_KEY=your_key_here`
5. Run `uvicorn main:app --reload`
6. Visit `http://localhost:8000`