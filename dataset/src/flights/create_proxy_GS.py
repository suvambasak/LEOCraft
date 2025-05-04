
'''
This script creates a proxy GS for each zone in the flight dataset.
It takes the center coordinates of the zone and counts the number of flights
and the number of passengers in the zone.
'''

import pandas as pd

FLIGHTS = flight_coordinates = pd.read_csv(
    'dataset/src/flights/dataset/flight_cluster.csv'
).to_dict(orient='records')


proxy_GS = dict()


for flight in FLIGHTS:

    # For each zone count the number of flights and the number of passengers
    # and take the center coordinates of the zone
    TAG = flight['tag']
    if TAG not in proxy_GS:
        proxy_GS[TAG] = dict()
        proxy_GS[TAG]['lat'] = 10 * (flight['lat']//10)
        proxy_GS[TAG]['lng'] = 10 * (flight['lng']//10)
        proxy_GS[TAG]['fcount'] = 0
        proxy_GS[TAG]['pop'] = 0

    proxy_GS[TAG]['fcount'] += 1
    proxy_GS[TAG]['pop'] += flight['passenger']

    print(f'|- {TAG} - {proxy_GS[TAG]}')

# Replace each zone with a proxy GS at center
proxy_GS_list = list()
for idx, item in enumerate(proxy_GS.items()):
    key, value = item
    proxy_GS_list.append({
        'id': idx,
        'tag': key,
        'lat': value['lat'],
        'lng': value['lng'],
        'pop': value['pop'],
        'fcount': value['fcount'],
    })


pd.DataFrame.from_dict(proxy_GS_list).to_csv(
    'dataset/src/flights/dataset/flight_proxy_GS.csv',
    index=False
)
