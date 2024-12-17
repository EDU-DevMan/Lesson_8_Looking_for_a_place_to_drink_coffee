import json
import requests
import folium

from decouple import config
from geopy import distance


APIKEY_YANDEX = config('apikey')


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = \
        response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def dict_coffee_list(user_coords, coffee_pars):
    coffee_new_list = []

    for pars in coffee_pars:
        distance_coffee = dict()
        distance_coffee['title'] = pars["Name"]
        distance_coffee['distance'] = distance.distance(
            (user_coords[1],
             user_coords[0]),
            (pars['geoData']['coordinates'][1],
             pars['geoData']['coordinates'][0])).km
        distance_coffee['latitude'] = pars['geoData']['coordinates'][1]
        distance_coffee['longitude'] = pars['geoData']['coordinates'][0]
        coffee_new_list.append(distance_coffee)

    return coffee_new_list


def get_user_distance(distance):
    return distance['distance']


def color_change(elev):
    if (elev < 1):
        return ('green')
    elif (1 <= elev < 3):
        return ('orange')
    else:
        return ('red')


def main():
    with open("files/coffee.json", "r", encoding="CP1251") as coffee:
        coffee_house = coffee.read()

    pars = json.loads(coffee_house)
    user_location = input('Где вы находитесь? ')
    coords = fetch_coordinates(APIKEY_YANDEX, user_location)

    m = folium.Map([coords[1], coords[0]], zoom_start=12)
    for values in sorted(dict_coffee_list(coords, pars),
                         key=get_user_distance)[:5]:

        folium.Marker(
            location=[values['latitude'], values['longitude']],
            tooltip="Look coffee",
            popup=values['title'],
            icon=folium.Icon(
                color=color_change(int(round(values['distance'])))),
        ).add_to(m)

    m.save("files/index.html")


if __name__ == '__main__':
    main()
