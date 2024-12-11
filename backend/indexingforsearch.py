import json

# Load the combined JSON file
with open('/Users/Intel/Desktop/Stat Final Project/alldata.json', 'r') as f:
    all_recipes = json.load(f)

# Create a dictionary to index recipes by title and ingredients
indexed_recipes = {}

for recipe in all_recipes:
    title = recipe.get("title", "").lower()
    ingredients = [ingredient.lower() for ingredient in recipe.get("ingredients", [])]
    
    # Index by title
    indexed_recipes[title] = recipe

    # Index by ingredients (create a list for each ingredient)
    for ingredient in ingredients:
        if ingredient not in indexed_recipes:
            indexed_recipes[ingredient] = []  # Initialize as a list if not already in index
        # Make sure the value at each index is a list before appending
        if isinstance(indexed_recipes[ingredient], list):
            indexed_recipes[ingredient].append(recipe)
        else:
            indexed_recipes[ingredient] = [recipe]  # Ensure we start with a list

# Save the indexed recipes to a new JSON file
with open('/Users/Intel/Desktop/Stat Final Project/indexed_recipes.json', 'w') as f:
    json.dump(indexed_recipes, f, indent=4)

print("Recipes indexed and saved to 'indexed_recipes.json'.")
