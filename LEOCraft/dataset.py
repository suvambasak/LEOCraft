class GroundStationAtCities:
    'Ground stations across most populous cities CSV dataset'

    TOP_100 = 'dataset/ground_stations/ground_stations_cities_sorted_by_estimated_2025_pop_top_100.csv'
    TOP_1000 = 'dataset/ground_stations/ground_stations_cities_sorted_by_estimated_2025_pop_top_1000.csv'


class InternetTrafficAcrossCities:
    '''Internet Traffic metrics using gravity model[1] across 100 and 1000 Ground stations
    - GDP Population (100 GS)
    - Population (100/1000 GS)

    Reference:
    1. Matthew Roughan. 2005. Simplifying the synthesis of internet traffic matrices. SIGCOMM Comput. Commun. Rev. 35, 5 (October 2005), 93–96. https://doi.org/10.1145/1096536.1096551
    '''

    POP_GDP_100 = 'dataset/traffic_metrics/population_GDP_tm_Gbps_100.json'
    ONLY_POP_100 = 'dataset/traffic_metrics/population_only_tm_Gbps_100.json'
    ONLY_POP_1000 = 'dataset/traffic_metrics/population_only_tm_Gbps_1000.json'


class FlightOnAir:
    '''Flight on air (> 10,000 feet) dataset clustered by 10 degree latitude and longitude grid

    Source: https://github.com/JeanExtreme002/FlightRadarAPI.git
    '''

    FLIGHT_REPLACED_TERMINALS = 'dataset/aircraft/flightReplacedGS.csv'
    FLIGHTS_CLUSTERS = 'dataset/aircraft/flightCluster.csv'


class InternetTrafficOnAir:
    '''Flight on air to ground station internet traffic metrics with gravity model[1]

    Reference:
    1. Matthew Roughan. 2005. Simplifying the synthesis of internet traffic matrices. SIGCOMM Comput. Commun. Rev. 35, 5 (October 2005), 93–96. https://doi.org/10.1145/1096536.1096551
    '''

    ONLY_POP_100 = 'dataset/air_traffic/flight_cluster_population_only_tm_100.json'
