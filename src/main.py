import argparse
from globals import PROJECT_ID, DATASET_NAME, A1_TABLE_ID, A2_TABLE_ID, A3_TABLE_ID
from geo_query import *

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-w", "--writer", help="enable for (over)writing results", action="store_true")
	args = parser.parse_args()
	gq = GeoQuery()
	if args.writer:
		gq.write_nearest_N_ports_to_base('jurong island', 5, '%s.%s.%s' % (PROJECT_ID, DATASET_NAME, A1_TABLE_ID))
		gq.write_country_with_most_ports_with_cargo_wharf('%s.%s.%s' % (PROJECT_ID, DATASET_NAME, A2_TABLE_ID))
		gq.write_nearest_viable_port_from_distress_call(32.610982, -38.706256, '%s.%s.%s' % (PROJECT_ID, DATASET_NAME, A3_TABLE_ID))
	gq.read_result_1()
	gq.read_result_2()
	gq.read_result_3()
