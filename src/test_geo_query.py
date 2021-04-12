import unittest
from mock import patch
from geo_query import GeoQuery
from globals import PROJECT_ID, DATASET_NAME, A1_TABLE_ID, A2_TABLE_ID, A3_TABLE_ID


def test_write_nearest_N_ports_to_base():
	"""
	Tests that _write_to_bq should be called exactly once, with expected args
	"""
	with patch.object(GeoQuery, '_write_to_bq', return_value=None) as mock_method:
	    gq = GeoQuery()
	    gq.write_nearest_N_ports_to_base('mybase', 3, 'nearest_to_base')
	    expected = """
			WITH base AS (
				SELECT st_geogpoint(port_longitude, port_latitude) FROM geographic.ports WHERE LOWER(port_name) = 'mybase'
			)
			SELECT 
				port_name, 
				ST_DISTANCE(st_geogpoint(port_longitude, port_latitude), (SELECT * FROM base)) AS distance_in_meters
			FROM geographic.ports 
			WHERE LOWER(port_name) NOT LIKE '%mybase%' -- don't include self
				-- AND country IN (NULL, 'SG', 'MY', 'PH', 'TH', 'ID', 'BN', 'PG') -- optimization only valid with the knowledge that ports beyond ASEAN region will not be close
			ORDER BY distance_in_meters ASC 
			LIMIT 3
			"""
	    mock_method.assert_called_once_with(expected, 'nearest_to_base')


def test_write_country_with_most_ports_with_cargo_wharf():
	"""
	Tests that _write_to_bq should be called exactly once, with expected args
	"""
	with patch.object(GeoQuery, '_write_to_bq', return_value=None) as mock_method:
	    gq = GeoQuery()
	    gq.write_country_with_most_ports_with_cargo_wharf('most_ports')
	    expected = """
			SELECT 
				country, 
				count(*) as port_count 
			FROM geographic.ports 
			WHERE cargo_wharf IS TRUE
			GROUP BY 1 
			ORDER BY port_count desc 
			LIMIT 1
			"""
	    mock_method.assert_called_once_with(expected, 'most_ports')


def test_write_nearest_viable_port_from_distress_call():
	"""
	Tests that _write_to_bq should be called exactly once, with expected args
	"""
	with patch.object(GeoQuery, '_write_to_bq', return_value=None) as mock_method:
	    gq = GeoQuery()
	    gq.write_nearest_viable_port_from_distress_call(30.6, -31.5, 'distress')
	    expected = """
			SELECT 
	            country,
				port_name, 
	            port_latitude,
	            port_longitude
			FROM geographic.ports 
	        WHERE water IS TRUE AND fuel_oil IS TRUE AND diesel IS TRUE
			ORDER BY ST_DISTANCE(st_geogpoint(port_longitude, port_latitude), st_geogpoint(-31.5, 30.6)) ASC
			LIMIT 1
			"""
	    mock_method.assert_called_once_with(expected, 'distress')


def test_read_result_1():
	"""
	Tests that the required columns are selected explicitly, and their IDs correspond to the global config
	"""
	with patch.object(GeoQuery, '_read_result', return_value=None) as mock_method:
		gq = GeoQuery()
		gq.read_result_1()
		expected = """SELECT port_name, distance_in_meters FROM {}.{}.{}""".format(PROJECT_ID, DATASET_NAME, A1_TABLE_ID)
		mock_method.assert_called_once_with(expected)


def test_read_result_2():
	"""
	Tests that the required columns are selected explicitly, and their IDs correspond to the global config
	"""
	with patch.object(GeoQuery, '_read_result', return_value=None) as mock_method:
		gq = GeoQuery()
		gq.read_result_2()
		expected = """SELECT country, port_count FROM {}.{}.{}""".format(PROJECT_ID, DATASET_NAME, A2_TABLE_ID)
		mock_method.assert_called_once_with(expected)


def test_read_result_3():
	"""
	Tests that the required columns are selected explicitly, and their IDs correspond to the global config
	"""
	with patch.object(GeoQuery, '_read_result', return_value=None) as mock_method:
		gq = GeoQuery()
		gq.read_result_3()
		expected = """SELECT country, port_name, port_latitude, port_longitude FROM {}.{}.{}""".format(PROJECT_ID, DATASET_NAME, A3_TABLE_ID)
		mock_method.assert_called_once_with(expected)