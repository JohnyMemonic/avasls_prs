import datetime
import gzip
import time
import random
import string
import time
import uuid
import hashlib
import json
import requests as rsk
import geoip2.database
from dotenv import load_dotenv
import redis
import logging
import os
from curl_cffi import requests


class ProxyNotAvailable(Exception):
    pass

def generate_device_id():
    return ''.join(random.choice(string.hexdigits).lower() for _ in range(16))


def generate_token():
    unique_id = uuid.uuid4()
    hashed_id = hashlib.md5(str(unique_id).encode()).hexdigest()
    return hashed_id


def generate_x_signature(request_body):
    uuid_str = "856890a7-59b2-4043-9bc7-e478bb4e6405"
    combined_string = uuid_str + str(request_body)
    x_signature = hashlib.md5(combined_string.encode()).hexdigest()
    return x_signature

url = 'https://tickets-api.aviasales.com/search/v2/start'

devices_id_list = [generate_device_id() for _ in range(3000)]


def get_data_from_api_avia(data_dict):

    device_id = random.choice(devices_id_list)
    generated_token = generate_token()
    request_body = {"search_params": {"directions": [
        {"origin": "LED", "destination": "MOW", "date": "2025-01-16",
         "is_origin_airport": False, "is_destination_airport": False},
        {"origin": "MOW", "destination": "LED", "date": "2025-01-25",
         "is_origin_airport": False, "is_destination_airport": False}],
        "passengers": {"adults": 1, "children": 0,
                       "infants": 0}, "trip_class": "Y"},
        "marker": f"mobile_app.{generated_token}", "citizenship": "RU",
        "market_code": "RU", "currency_code": "RUB", "languages": {"ru": 1.0},
        "gates_to_request": [], "exact_tickets": [], "debug": {},
        "experiment_groups": {
            "serp-exp-hotelsSearchAutostart": "on_with_tooltip",
            "ex-exp-autocompleteGeolocationHint": "treatment",
            "ex-exp-autocompleteRecommendations": "destination",
            "ex-feat-mainPromoKoroche": "on",
            "ex-exp-calendarWithoutInputs": "on", "ex-exp-mainCityVideo": "off",
            "ex-exp-flexDatesAi": "off", "ex-exp-flexiblePresets": "off",
            "ex-feat-hottickets": "on-v2",
            "ex-exp-hotTicketsDefaultTripType": "control",
            "ex-exp-interstitial-ads": "ads-free_users",
            "ex-feat-nationalParksAutocomplete": "off",
            "ex-exp-nearby-airports-autocomplete": "on",
            "ex-feat-easterEgg2025": "on", "ex-feat-requestGeolocation": "on",
            "ex-exp-searchFormClearNavigation": "on",
            "ex-exp-searchFormRefactoring": "on",
            "guides-exp-trapDirectNavigation": "content",
            "guides-exp-walksFeedPosition": "c",
            "avs-mon-exp-hotelNavigation": "variant_b",
            "serp-exp-hotelsBannerOnTicket": "on",
            "serp-exp-hotelsMapResultsSync": "on", "serp-exp-hotels": "off",
            "prem-exp-landingV3AviacashbackOffer": "off",
            "badges_redesign_2": "new_badges", "asb-exp-saloOtaRuler": "ota",
            "serp-exp-autosearchAllBadges": "on", "serp-exp-captcha": "on",
            "serp-exp-composeTicketScreen": "off",
            "serp-exp-directFlightsCompose": "off",
            "serp-exp-faqInTicket": "off", "serp-exp-faresV2": "on",
            "serp-exp-replaceFares": "off", "serp-exp-filtersShortcuts": "off",
            "serp-exp-flexibleFaresPromo": "on",
            "serp-feat-aviaCashback": "off", "serp-exp-serverFilters": "on",
            "avs-exp-foreignCards": "on", "serp-exp-savedFilters": "on",
            "serp-exp-serverSecondaryBadges": "off",
            "serp-exp-ticketNavigation": "off", "serp-exp-ticketAnchor": "off",
            "serp-exp-drawerAsWidget": "off", "serp-exp-headOfTicket": "off",
            "serp-exp-ticketInExpiredSearch": "off",
            "serp-exp-ticketPolling": "off", "serp-exp-uxFeedback": "off",
            "serp-exp-virtualInterlineInsurance": "off",
            "serp-exp-interlinesRebranding": "off",
            "serp-exp-serverBannersOnTicket": "on",
            "asb-exp-showAssistedSaloEdition": "on",
            "usc-flag-DefinitionCurrencyAndCountryDialog": "control"},
        "brand": "AS", "premium": None, "payment_options": [],
        "search_source": "explore-exact",
        "filters": {"prechecks": None, "directions_saved": []}}

    request_body["search_params"]["passengers"] = {}
    request_body["search_params"]["passengers"]["adults"] = data_dict["travelers"].get(
        "adult", 0)
    request_body["search_params"]["passengers"]["children"] = data_dict[
        "travelers"].get(
        "child", 0)
    request_body["search_params"]["passengers"]["infants"] = data_dict["travelers"].get(
        "infant", 0)
    request_body['search_params']['directions'] = []
    for trip in data_dict['trips']:
        direction = {
            "origin": trip['departure'],
            "destination": trip['arrival'],
            "date": trip['departure_date'],
            "is_origin_airport": False,
            "is_destination_airport": False
        }
        request_body['search_params']['directions'].append(direction)
    request_body = json.dumps(request_body)
    x_signature = generate_x_signature(request_body)
    logging.info(x_signature)

    headers = {
        'x-signature': f'aviasales.mobile.android:{x_signature}',
        'accept-encoding': 'br,gzip',
        'x-client-type': 'mobile',
        'referer': 'https://phone.android.aviasales.gb',
        'client-device-info': f'application=Aviasales; version=6.46.0; device_id={device_id}; device_model=Galaxy+S8%2B; type=mobile; os=android; os_api_level=26; os_version=8.0.0; mobile_country_code=250; mobile_network_code=02; network=wifi; token={generated_token}; generated_token={generated_token}; host=phone.android.aviasales.gb; system_region=GB',
        'user-agent': 'Aviasales/6.46.0',
        'content-type': 'application/json; charset=utf-8',
        'content-length': str(len(request_body)),
    }

    response = requests.post(url, headers=headers, data=request_body,
                             impersonate='chrome')

    logging.info(response.text)
    if response.json().get('type') in ('invalid-arguments', 'invalid-date'):
        return response.json()

    response_data = response.json()
    searchId = response_data.get('search_id')
    results_url = response_data.get('results_url')

    results_url = f'https://{results_url}/search/v3.1/results'

    request_body = {
        "search_id": searchId,
        "limit": 350,
        "last_update_timestamp": 0,
        "required_tickets": [],
        "search_by_airport": False,
        "price_per_person": False,
        "filters_state": {
            "transfers_count": ["0", "1"]
        }
    }

    headers = {
        'accept-encoding': 'br,gzip',
        'x-client-type': 'mobile',
        'referer': 'https://phone.android.aviasales.gb',
        'client-device-info': f'application=Aviasales; version=6.46.0; device_id={device_id}; device_model=Galaxy+S8%2B; type=mobile; os=android; os_api_level=26; os_version=8.0.0; mobile_country_code=250; mobile_network_code=02; network=wifi; token={generated_token}; generated_token={generated_token}; host=phone.android.aviasales.gb; system_region=GB',
        'user-agent': 'Aviasales/6.46.0',
        'content-type': 'application/json; charset=utf-8',
    }

    n = 0
    while n < 10:
        time.sleep(2)
        response = requests.post(results_url, headers=headers, json=request_body,
                                 impersonate='chrome')
        data = response.json()
        if data[0].get('last_update_timestamp') == 0:
            break
        n += 1
    return response.json()


def start(tiket_param, data_dict):
    try:
        logging.info(f'Start {tiket_param}')
        result = get_data_from_api_avia(data_dict)
        json_bytes = json.dumps(result).encode('utf-8')
        compressed_data = gzip.compress(json_bytes)
        return compressed_data
    finally:
        pass


if __name__ == '__main__':
    start_time = datetime.datetime.now()
    data = {
        "cabin_class": "economy",
        "travelers": {
            "adult": 1,
            "child": 0,
            "infant": 0
        },
        "trips": [
            {
                "departure": "MOW",
                "arrival": "LED",
                "departure_date": "2026-11-06"
            }
        ]
    }
    x = start("MOW0611LED", data)
    with open('test_data.json', 'w') as f:
        f.write(f"{x}")
    print(x)
    print(datetime.datetime.now() - start_time)
