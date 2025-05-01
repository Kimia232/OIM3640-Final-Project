from flask import Flask, render_template, request
from datetime import datetime
import requests

app = Flask(__name__)

# Fetch the real list of ingredients from CocktailDB API
def get_ingredients():
    url = "https://www.thecocktaildb.com/api/json/v1/1/list.php?i=list"
    response = requests.get(url)
    ingredients = []
    if response.status_code == 200:
        data = response.json()
        if isinstance(data.get('drinks'), list):
            ingredients = [item['strIngredient1'] for item in data['drinks']]
    return ingredients

# Fetch a random cocktail
def get_random_cocktail():
    try:
        url = "https://www.thecocktaildb.com/api/json/v1/1/random.php"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data.get('drinks'), list):
                return data['drinks'][0]  # Return the first (and only) random drink
        return None
    except Exception as e:
        print(f"Error fetching random cocktail: {e}")
        return None

# Calculate age
def calculate_age(birthdate_str):
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

# Homepage
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        birthdate = request.form['birthdate']
        if calculate_age(birthdate) >= 21:
            ingredients = get_ingredients()
            random_cocktail = get_random_cocktail()   # ✨ Fetch random cocktail
            return render_template('choices.html', ingredients=ingredients, random_cocktail=random_cocktail)   # ✨ Pass it
        else:
            return "Sorry, you must be 21 or older to use this app."
    return render_template('index.html')


# Search
@app.route('/search', methods=['POST'])
def search():
    search_type = request.form.get('search_type')

    if search_type == 'name':
        query = request.form.get('query_name', '').strip()
    else:
        query = request.form.get('query_alcohol', '').strip()

    base_url = "https://www.thecocktaildb.com/api/json/v1/1/"
    drinks = []

    if search_type == 'name':
        query = " ".join(word.capitalize() for word in query.split())
        url = base_url + f"search.php?s={query}"
        print(f"Searching by drink name: {url}")
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data.get('drinks'), list):
                drinks = [drink for drink in data['drinks'] if drink.get('strDrink') and drink.get('strInstructions')]

    elif search_type == 'alcohol':
        url = base_url + f"filter.php?i={query}"
    print(f"Searching by alcohol: {url}")
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if isinstance(data.get('drinks'), list):
            for item in data['drinks']:
                if isinstance(item, dict):
                    drink_id = item.get('idDrink')
                    if drink_id:
                        # LOOKUP full details for the drink
                        lookup_url = base_url + f"lookup.php?i={drink_id}"
                        lookup_response = requests.get(lookup_url)
                        if lookup_response.status_code == 200:
                            lookup_data = lookup_response.json()
                            if isinstance(lookup_data.get('drinks'), list):
                                drinks.append(lookup_data['drinks'][0])


    drinks = [drink for drink in drinks if drink.get('strDrink') and drink.get('strInstructions')]

    print(f"Total drinks found: {len(drinks)}")
    return render_template('result.html', drinks=drinks)

if __name__ == '__main__':
    app.run(debug=True)