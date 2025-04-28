from flask import Flask, render_template, request
from datetime import datetime
import requests

app = Flask(__name__)

RELIABLE_ALCOHOLS = [
    "Vodka", "Light Rum", "Dark Rum", "Gin", "Tequila",
    "Whiskey", "Brandy", "Amaretto", "Triple Sec", "Baileys Irish Cream",
    "Scotch", "Cognac", "Kahlua", "Campari"
]

def calculate_age(birthdate_str):
    birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        birthdate = request.form['birthdate']
        if calculate_age(birthdate) >= 21:
            return render_template('choices.html', alcohols=RELIABLE_ALCOHOLS)
        return "Sorry, you must be 21 or older to use this app."
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_type = request.form['search_type']
    query = " ".join(word.capitalize() for word in request.form['query'].strip().split())

    url = f"https://www.thecocktaildb.com/api/json/v1/1/{'search.php?s=' if search_type == 'name' else 'filter.php?i='}{query}"
    response = requests.get(url)

    if response.status_code != 200:
        return "Failed to fetch cocktails."

    data = response.json()
    drinks = []

    if data.get('drinks'):
        if search_type == 'alcohol':
            for item in data['drinks']:
                drink_id = item.get('idDrink')
                detail = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={drink_id}").json()
                if detail.get('drinks'):
                    drinks.append(detail['drinks'][0])
        else:
            drinks = data['drinks']

    # Only show drinks with names and instructions
    drinks = [drink for drink in drinks if drink.get('strDrink') and drink.get('strInstructions')]

    return render_template('result.html', drinks=drinks)

if __name__ == '__main__':
    app.run(debug=True)
