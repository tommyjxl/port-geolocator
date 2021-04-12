from google.cloud import bigquery
from globals import PROJECT_ID, DATASET_NAME, A1_TABLE_ID, A2_TABLE_ID, A3_TABLE_ID

def print_rows(results):
	"""
	Helper function to print query results
	"""
	print('--- Result Summary ---')
	for row in results:
		r = []
		for i in range(0, len(row)):
			r.append(str(row[i]))
		print(', '.join(r))
	print('--- End ---')


class GeoQuery():
	"""
	Queries to write and read port data to/from BigQuery 
	"""
	def __init__(self):
		self.client = bigquery.Client()

	def _write_to_bq(self, sql, table_id):
		"""
		Write results of SQL statement to BQ, overwrites existing table if exists
		"""
		job_config = bigquery.QueryJobConfig(allow_large_results=True, destination=table_id, write_disposition='WRITE_TRUNCATE')
		query_job = self.client.query(sql, job_config=job_config)
		return query_job.result()

	def write_nearest_N_ports_to_base(self, base_port, max_port_count, table_id):
		"""
		Write the result of the query which finds the nearest N ports to a base port
		"""
		sql = """
			WITH base AS (
				SELECT st_geogpoint(port_longitude, port_latitude) FROM geographic.ports WHERE LOWER(port_name) = '{base_port}'
			)
			SELECT 
				port_name, 
				ST_DISTANCE(st_geogpoint(port_longitude, port_latitude), (SELECT * FROM base)) AS distance_in_meters
			FROM geographic.ports 
			WHERE LOWER(port_name) NOT LIKE '%{base_port}%' -- don't include self
				-- AND country IN (NULL, 'SG', 'MY', 'PH', 'TH', 'ID', 'BN', 'PG') -- optimization only valid with the knowledge that ports beyond ASEAN region will not be close
			ORDER BY distance_in_meters ASC 
			LIMIT {max_port_count}
			""".format(base_port=base_port, max_port_count=max_port_count)
		return self._write_to_bq(sql, table_id)

	def write_country_with_most_ports_with_cargo_wharf(self, table_id):
		"""
		Write the result of the query which finds the country with the most ports with a cargo wharf
		"""
		sql = """
			SELECT 
				country, 
				count(*) as port_count 
			FROM geographic.ports 
			WHERE cargo_wharf IS TRUE
			GROUP BY 1 
			ORDER BY port_count desc 
			LIMIT 1
			"""
		return self._write_to_bq(sql, table_id)

	def write_nearest_viable_port_from_distress_call(self, latitude, longitude, table_id):
		"""
		Write the result of the query which finds the nearest viable port from a distress call with specified latitude and longitude
		"""
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
			""".format(latitude=latitude, longitude=longitude)
		return self._write_to_bq(sql, table_id)

	def _read_result(self, sql):
		"""
		Query and print the result of a select statement
		"""
		client = bigquery.Client()
		query_job = self.client.query(sql)
		print('Query: ' + sql)
		results = query_job.result()
		print_rows(results)

	def read_result_1(self):
		"""
		Read result for Question 1
		"""
		self._read_result("""SELECT port_name, distance_in_meters FROM {}.{}.{}""".format(PROJECT_ID, DATASET_NAME, A1_TABLE_ID))
	
	def read_result_2(self):
		"""
		Read result for Question 2
		"""
		self._read_result("""SELECT country, port_count FROM {}.{}.{}""".format(PROJECT_ID, DATASET_NAME, A2_TABLE_ID))

	def read_result_3(self):
		"""
		Read result for Question 3
		"""
		self._read_result("""SELECT country, port_name, port_latitude, port_longitude FROM {}.{}.{}""".format(PROJECT_ID, DATASET_NAME, A3_TABLE_ID))
