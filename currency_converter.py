import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from xml.etree import ElementTree as ET

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/currency_converter', methods=['GET'])
def convert_currency():
    amount = float(request.args.get('amount', default=0))
    from_currency = request.args.get('from_currency')
    to_currency = request.args.get('to_currency')

    rates = fetch_currency_rates()
    if not rates:
        return jsonify({'error': 'Failed to fetch currency rates from ECB'})

    conversion_rate = get_conversion_rate(rates, from_currency, to_currency)
    if not conversion_rate:
        return jsonify({'error': 'Invalid currency conversion'})

    result = amount * conversion_rate

    response = {
        'amount': amount,
        'from_currency': from_currency,
        'to_currency': to_currency,
        'result': result
    }

    return jsonify(response)


def fetch_currency_rates():
    response = requests.get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
    if response.status_code == 200:
        rates = parse_currency_rates(response.content)
        return rates
    else:
        return None


def parse_currency_rates(response_xml):
    root = ET.fromstring(response_xml)
    cube_elements = root.findall('.//{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube/{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube')
    currency_rates = {}
    for cube in cube_elements:
        currency = cube.attrib.get('currency')
        rate = cube.attrib.get('rate')
        if currency and rate:
            currency_rates[currency] = float(rate)
    return currency_rates


def get_conversion_rate(rates, from_currency, to_currency):
    if from_currency == 'EUR':
        return rates.get(to_currency)
    elif to_currency == 'EUR':
        return 1 / rates.get(from_currency)
    else:
        return rates.get(to_currency) / rates.get(from_currency) # cross calculation of rates


if __name__ == '__main__':
    app.run()
