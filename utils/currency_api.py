# utils/currency_api.py
import requests 

def get_exchange_rate(base_currency, target_currency):
    """Fetch the real-time exchange rate from an API."""
    url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
    response = requests.get(url)
    data = response.json()

    if "rates" in data and target_currency in data["rates"]:
        return data["rates"][target_currency]
    else:
        return None
    