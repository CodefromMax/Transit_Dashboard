from calculation.travel_time_matrix.TravelTimeCalculation import TravelTimeCalculation

print('Building Transport Network')
ttc = TravelTimeCalculation("/Users/user/Documents/Capstone/Transit_Dashboard/data/OSM_data/Toronto.osm.pbf", "/Users/user/Documents/Capstone/Transit_Dashboard/backend/src/gtfs_output.zip")
ttc.build_transport_network()
print(ttc.transport_network)
print('Done')