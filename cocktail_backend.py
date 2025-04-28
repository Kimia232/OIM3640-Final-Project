from flask import Flask, render_template, request
from datetime import datetime
import requests

app = Flask(__name__)

# Reliable alcohol list
RELIABLE_ALCOHOLS = [
    "Vodka", "Light Rum", "Dark Rum", "Gin", "Tequila",
    "Whiskey", "Brandy", "Amaretto", "Triple Sec", "Baileys Irish Cream",
    "Scotch", "Cognac", "Kahlua", "Campari"
]

# Age calculator
def calculate_age(birthdate_str):
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

# Home page: Enter birthday
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        birthdate = request.form['birthdate']
        age = calculate_age(birthdate)
        if age >= 21:
            return render_template('choices.html', alcohols=RELIABLE_ALCOHOLS)
        else:
            return "Sorry, you must be 21 or older to use this app."
    return render_template('index.html')

# Search page
@app.route('/search', methods=['POST'])
def search():
    search_type = request.form['search_type']
    query = request.form['query'].strip()

    if search_type == 'alcohol':
        query = " ".join(word.capitalize() for word in query.split())

    if search_type == 'name':
        url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={query}"
    elif search_type == 'alcohol':
        url = f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={query}"
    else:
        return "Invalid search option selected."

    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to fetch data from API."

    try:
        data = response.json()
    except Exception as e:
        print("⚠️ JSON Error:", e)
        return "Bad response from API."

    drinks = []

    if data.get('drinks'):
        if search_type == 'alcohol':
            # Look up each drink ID for full details
            for item in data['drinks']:
                if isinstance(item, dict) and 'idDrink' in item:
                    drink_id = item['idDrink']
                    detail_url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}"
                    detail_res = requests.get(detail_url)
                    if detail_res.status_code == 200:
                        detail_data = detail_res.json()
                        if detail_data.get('drinks'):
                            drinks.append(detail_data['drinks'][0])
        else:
            # For drink name search, no extra lookup needed
            drinks = data['drinks']

    # ⚡ FINAL SAFETY: Only show if title+instructions exist
    final_drinks = []
    for drink in drinks:
        if drink.get('strDrink') and drink.get('strInstructions'):
            final_drinks.append(drink)

    return render_template('result.html', drinks=final_drinks)

if __name__ == '__main__':
    app.run(debug=True)
