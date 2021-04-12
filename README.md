# port-geolocator
Write and/or read queries on global seaport and airport data

## Local machine set-up (Mac OS)
Install Python 3.8.6 or higher: https://www.python.org/downloads/mac-osx/

Install gcloud: https://cloud.google.com/sdk/docs/quickstart

From port-geolocator directory, install Python dependencies.
`pip install --upgrade -r requirements.txt`

Ensure that 
Ensure that your service account key JSON file is on your local machine and that your environment variable GOOGLE_APPLICATION_CREDENTIALS is the correct path to the file.

`printenv GOOGLE_APPLICATION_CREDENTIALS`
should show something like /path/to/service_account_key.json

Set project and confirm that it has been set.
`gcloud config set project sandbox-experiments-only`
`gcloud config get-value project` 

## Running the script
For reading the results only:
`python main.py`

For overwriting the result tables, then reading the results (requires write permission from GCP IAM):
`python main.py --writer`

The output is found in the resulting dataset and table_ids specified in main.py and also printed to the console.

## Unit Tests
`pytest test_geo_query.py`

## Visualisation (Optional)
Ensure that geopandas is installed: https://geopandas.org/getting_started/install.html
The preferred way is to install from source.
Version used: 0.9.0+12.gafa49e0

Ensure these dependencies are installed:
`pip install matplotlib==3.3.2`
`pip install shapely`

Running the script:
`python visualisation.py`

The visualisation graphic will automatically display, close the window(s) to complete the script.
Results can also be found in the port-geolocator/output directory.

Visualisation reference files:
- Geopandas built-in world map
- DataGov.sg National Map Polygon: https://data.gov.sg/dataset/national-map-polygon?resource_id=d1f2a8b0-a618-4b8e-be48-d90c3e34d746
