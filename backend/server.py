import requests
from flask import Flask, request, jsonify, render_template
import json
from rapidfuzz import process
import os
import openai 
from dotenv import load_dotenv

# Initialize Flask app
app = Flask(__name__)

# Public URL of the Google Cloud Storage file
INDEXED_RECIPES_URL = "https://storage.googleapis.com/recipe-storage/indexed_recipes.json"  # Replace <BUCKET_NAME> with your bucket name.

# Load the indexed recipes from Google Cloud Storage
try:
    response = requests.get(INDEXED_RECIPES_URL)
    response.raise_for_status()  # Raise an error for bad status codes
    indexed_recipes = response.json()  # Parse the JSON content
except Exception as e:
    indexed_recipes = {}
    print(f"Error loading indexed_recipes.json: {e}")

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Make sure your OpenAI API key is set correctly

# Search recipe by title with fuzzy matching
def search_recipe_by_title(query):
    query = query.lower()
    closest_match = process.extractOne(query, indexed_recipes.keys(), score_cutoff=70)  # Adjust score_cutoff as needed
    if closest_match:
        return indexed_recipes[closest_match[0]]
    return None

# Function to generate a recipe suggestion or chatbot response using OpenAI
def generate_recipe_suggestion(query):
    try:
        # Use OpenAI to generate a response based on the user query
        response = openai.Completion.create(
            model="text-davinci-003",  # You can replace this with a different model like GPT-4 if you have access
            prompt=f"Provide a recipe suggestion for: {query}",
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating recipe suggestion: {e}")
        return None

# Search for a recipe via GET request (from the browser)
@app.route('/get_recipe', methods=['GET'])
def get_recipe_get():
    query = request.args.get('query')  # Accept query from URL
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # Search for recipes based on query
    recipe = search_recipe_by_title(query)
    print(f"Recipe found: {recipe}")  # Debugging output to verify the data

    if recipe:
        # If a list is returned, pass the list; otherwise, pass the dictionary
        return render_template('recipe_result.html', recipe=recipe if isinstance(recipe, list) else [recipe])
    else:
        # If no recipe is found, generate a suggestion using OpenAI
        suggestion = generate_recipe_suggestion(query)
        if suggestion:
            return render_template('recipe_result.html', recipe={"title": suggestion, "ingredients": suggestion})
        else:
            return render_template('recipe_result.html', recipe=None)  # If no recipe and no suggestion

# Home page with search bar
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
