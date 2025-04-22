from flask import Flask, render_template, request
from datetime import datetime
import requests

app = Flask(__name__)

# Utility to calculate age
def calculate_age(birthdate_str):
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

# Get valid drink names and reliable alcohol ingredients
def get_dropdown_options():
    valid_drinks = set()
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}"
        try:
            res = requests.get(url).json()
            drinks = res.get('drinks')
            if drinks:
                for drink in drinks:
                    name = drink.get('strDrink')
                    if name:
                        verify_url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}"
                        check = requests.get(verify_url).json()
                        if check.get('drinks'):
                            valid_drinks.add(name)
        except Exception as e:
            print(f"Skipping drink letter {letter}: {e}")

    # ✅ Use a manually curated list of reliable base alcohols
    reliable_alcohols = [
    "Vodka", "Rum", "Gin", "Tequila", "Whiskey",
    "Brandy", "Amaretto", "Triple Sec", "Bailey's Irish Cream",
    "Scotch", "Cognac", "Kahlua", "Campari"
]

    return sorted(valid_drinks), sorted(reliable_alcohols)

# Home route — asks for birthday
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        birthdate = request.form['birthdate']
        age = calculate_age(birthdate)
        if age >= 21:
            drink_names, alcohols = get_dropdown_options()
            return render_template('choices.html', drink_names=drink_names, alcohols=alcohols)
        else:
            return "Sorry, you must be 21 or older to use this app."
    return render_template('index.html')

# Handles search for cocktails by name or alcohol
@app.route('/search', methods=['POST'])
def search():
    search_type = request.form['search_type']
    query = request.form['query'].strip().lower()

    print("🔍 SEARCH TYPE:", search_type)
    print("🔍 QUERY (raw):", query)

    if search_type == 'name':
        url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={query}"
    elif search_type == 'alcohol':
        # Capitalize each word (e.g., 'baileys irish cream' -> 'Baileys Irish Cream')
        normalized = " ".join(word.capitalize() for word in query.split())
        url = f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={normalized}"
    else:
        return "Invalid search option selected."

    print("🔗 API URL:", url)

    response = requests.get(url)
    data = response.json()

    drinks = []
    if search_type == 'alcohol' and data.get('drinks'):
        for item in data['drinks']:
            if isinstance(item, dict) and 'idDrink' in item:
                drink_id = item['idDrink']
                detail_url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}"
                detail_res = requests.get(detail_url)
                detail_data = detail_res.json()
                if detail_data.get('drinks'):
                    drinks.append(detail_data['drinks'][0])
    else:
        drinks = data.get('drinks', [])

    print("✅ RESULTS FOUND:", len(drinks))
    return render_template('result.html', drinks=drinks)

if __name__ == '__main__':
    app.run(debug=True)
