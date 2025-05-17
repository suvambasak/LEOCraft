# Modeling of Internet Traffic Matrics (TMs)

## Datasets

- [World cities](./ground_stations/CSVs/raw/worldcities.csv)
- [List of cities by GDP](./ground_stations/CSVs/raw/List_of_cities_by_GDP_2.csv)
- [Country capitals](./ground_stations/CSVs/raw/country-capital-lat-long-population.csv)
- [flight on air](./flights/dataset/flight_dataset.csv)
- [Passenger capacilty by model name](./flights/dataset/max_passenger_capacity.json)

## Data Sources

- [Flights](https://jeanextreme002.github.io/FlightRadarAPI/python/)
- [GDP](https://www.kaggle.com/datasets/khushikhushikhushi/global-cities-by-gdp)
- [World Cities Database](https://simplemaps.com/data/world-cities)
- [Country capitals](https://gist.github.com/ofou/df09a6834a8421b4f376c875194915c9)


## GDP and Population TMs

### Target market share is 10\% of the population

$$  P = \sum_{g=1}^G population_i \times 10\% $$

### Adding GDP weight ($GW_g$)

$$ GW_g = P \times \frac{GDP_g}{\sum GDP_g} $$

### Adding 300 Kbps data rate per head

$$ T_g = GW_g \times 300 Kbps $$


### Traffic demand acorss cities ($TM_{g,h}$)

$$ TM_{g,h} = T_g \times \frac{1/geodesic_{g,h}}{\sum_i^G 1/geodesic_{g,i}} $$


## Only Population TMs

### Target market share is 10\% of the population

$$  P_g = population_g \times 10\% $$ 

### Adding 300 Kbps data rate per head

$$ T_g = P_g \times 300 Kbps $$


### Traffic demand acorss cities ($TM_{g,h}$)


$$ TM_{g,h} = T_g \times \frac{1/geodesic_{g,h}}
{\sum_i^G 1/geodesic_{g,i}} $$



## Ground Stations to Flights TMs

### Ground population share and demand

$$p_g = population_g \times 10\%$$
$$T_g = p_g \times 300 Kbps$$


### Flight passenger share and demand

$$p_f = population_f \times 50\%$$
$$T_f = p_f \times 300 Kbps$$

### Traffic demand acorss ground and flights ($TM_{g,f}$)

$$ TM_{g,f} = (T_g \times \frac{1/geo_{g,f}}{\sum_i^F 1/geo_{g,i}}) + (T_f \times \frac{1/geo_{g,f}}{\sum_i^G 1/geo_{i,f}}) $$


## Datasets used by LEOCraft

## Ground station locations

- [100 GSes](../ground_stations/cities_sorted_by_estimated_2025_pop_top_100.csv)
- [1000 GSes](../ground_stations/cities_sorted_by_estimated_2025_pop_top_1000.csv)
- [Country capital GSes](../ground_stations/country_capitals.csv)


## Flight locations

- [Flight cluster](../aircraft/flightCluster.csv)
- [Proxy GS for flight cluster](../aircraft/flightReplacedGS.csv)


## Traffic matrics

- [Population and GDP weighed acorss 100 GSes](../traffic_metrics/population_GDP_tm_Gbps_100.json)
- [Population weighed acorss 100 GSes](../traffic_metrics/population_only_tm_Gbps_100.json)
- [Population weighed acorss 1000 GSes](../traffic_metrics/population_only_tm_Gbps_1000.json)
- [Population weighed acorss capitals GSes](../traffic_metrics/country_capital_population_only_tm.json)
- [Flights with 300 Kbps](../air_traffic/flight_cluster_population_only_tm_100_300Kbps.json)
- [Flights with 5 mbps](../air_traffic/flight_cluster_population_only_tm_100_5Mbps.json)