import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from google.cloud import bigquery
from globals import PROJECT_ID, DATASET_NAME, A1_TABLE_ID, DISTRESS_CALL_LATITTUDE, DISTRESS_CALL_LONGITUDE
from geo_query import GeoQuery
from shapely.geometry import Point, LineString


def visualise_ports_near_jurong_island():
	"""
	Visualise the nearby ports to Jurong Island
	"""
	client = bigquery.Client()
	MAX_COUNT = 6
	sql = """
		WITH base AS (
			SELECT st_geogpoint(port_longitude, port_latitude) FROM geographic.ports WHERE LOWER(port_name) = '{base_port}'
		)
		SELECT 
			port_name, 
			port_latitude,
			port_longitude,
			ST_DISTANCE(st_geogpoint(port_longitude, port_latitude), (SELECT * FROM base)) AS distance_in_meters
		FROM geographic.ports 
		WHERE country IN (NULL, 'SG', 'MY', 'PH', 'TH', 'ID', 'BN', 'PG') -- optimization only valid with the knowledge that ports beyond ASEAN region will not be close
		ORDER BY distance_in_meters ASC 
		LIMIT {max_port_count}
		""".format(base_port='jurong island', max_port_count=MAX_COUNT)
	lats = []
	longs = []
	results = client.query(sql).result()
	for row in results:
		lats.append(row.port_latitude)
		longs.append(row.port_longitude)

	df = pd.DataFrame(list(zip(lats, longs)), columns =['latitude', 'longitude'])
	geom = gpd.points_from_xy(df.longitude, df.latitude)

	lines = []
	for i in range(1, MAX_COUNT):
		lines.append(LineString([Point(geom[0].x, geom[0].y), (geom[i].x, geom[i].y)]))

	points = []
	for i in range(1, MAX_COUNT):
		points.append(Point(geom[i].x, geom[i].y))

	gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries(lines))
	d2_map = gpd.read_file('../data/national-map-polygon-geojson.geojson')
	ax = d2_map.plot(
	    color='white', edgecolor='black', linewidth=1, zorder=1)
	gdf.plot(ax=ax, color='green', linewidth=1, markersize=1, zorder=2)
	gdf2 = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries(points))
	gdf2.plot(ax=ax, color='green', markersize=10, zorder=3)
	gdf3 = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries([Point(geom[0].x, geom[0].y)]))
	gdf3.plot(ax=ax, color='red', markersize=10, zorder=4)
	plt.savefig('../output/ports_near_jurong_island.png')
	plt.show()


def visualise_distress_call_incident():
	"""
	Visualise the distress call location and the nearest port with neccessary resources
	"""
	world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
	client = bigquery.Client()
	sql = """
		SELECT 
            country,
			port_name, 
            port_latitude,
            port_longitude
		FROM geographic.ports 
        WHERE water IS TRUE AND fuel_oil IS TRUE AND diesel IS TRUE
		ORDER BY ST_DISTANCE(st_geogpoint(port_longitude, port_latitude), st_geogpoint({longitude}, {latitude})) ASC
		LIMIT 1
		""".format(latitude=DISTRESS_CALL_LATITTUDE, longitude=DISTRESS_CALL_LONGITUDE)
	results = client.query(sql).result()
	lats = [DISTRESS_CALL_LATITTUDE] 
	longs = [DISTRESS_CALL_LONGITUDE]
	for row in results:  # only 1 row expected
		lats.append(row.port_latitude)
		longs.append(row.port_longitude)

	df = pd.DataFrame(list(zip(lats, longs)), columns =['latitude', 'longitude'])
	geom = gpd.points_from_xy(df.longitude, df.latitude)

	lines = [LineString([Point(geom[0].x, geom[0].y), (geom[1].x, geom[1].y)])]
	gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries(lines))

	ax = world.plot(
	    color='white', edgecolor='black', linewidth=1, zorder=1)

	gdf.plot(ax=ax, color='green', linewidth=1, markersize=1, zorder=2)
	gdf2 = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries([Point(geom[1].x, geom[1].y)]))
	gdf2.plot(ax=ax, color='green', markersize=10, zorder=3)
	gdf3 = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries([Point(geom[0].x, geom[0].y)]))
	gdf3.plot(ax=ax, color='red', markersize=10, zorder=4)
	plt.savefig('../output/distress_call.png')
	plt.show()


if __name__ == "__main__":
	visualise_ports_near_jurong_island()
	visualise_distress_call_incident()
	
