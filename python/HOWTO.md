# Howto

## Using memcached from Python

* [Good examples of python-memcache (memcached) being used in Python?](http://stackoverflow.com/questions/868690/good-examples-of-python-memcache-memcached-being-used-in-python)

## Data import (OSM, Denmark, epsg:3857)

Download and unpack:

	wget http://download.cloudmade.com/europe/northern_europe/denmark/denmark.shapefiles.zip
	unzip denmark.shapefiles.zip
	ls -1 denmark.shapefiles
	# denmark.shapefiles/denmark_administrative.shp
	# denmark.shapefiles/denmark_coastline.shp
	# denmark.shapefiles/denmark_highway.shp
	# denmark.shapefiles/denmark_location.shp
	# denmark.shapefiles/denmark_natural.shp
	# denmark.shapefiles/denmark_poi.shp
	# denmark.shapefiles/denmark_water.shp

Check Postgres/PostGIS version:

	# Postgres should be 9.1+
	psql -d openstreetmap_3857 -h localhost -U postgres -t -c 'select version();'
	# PostGIS version should be 2.0+
	psql -d openstreetmap_3857 -h localhost -U postgres -t -c 'select PostGIS_full_version();'

Prepare database:

	psql -d openstreetmap_3857 -h localhost -U postgres 'create extension postgis;'

Create sql:

	mkdir denmark.pg
	shp2pgsql -s 4326:3857 -I denmark.shapefiles/denmark_administrative.shp denmark_administrative > denmark.pg/denmark_administrative.sql
	shp2pgsql -s 4326:3857 -I denmark.shapefiles/denmark_coastline.shp denmark_coastline > denmark.pg/denmark_coastline.sql
	shp2pgsql -s 4326:3857 -I denmark.shapefiles/denmark_highway.shp denmark_highway > denmark.pg/denmark_highway.sql
	shp2pgsql -s 4326:3857 -I denmark.shapefiles/denmark_location.shp denmark_location > denmark.pg/denmark_location.sql
	shp2pgsql -s 4326:3857 -I denmark.shapefiles/denmark_natural.shp denmark_natural > denmark.pg/denmark_natural.sql
	shp2pgsql -s 4326:3857 -I denmark.shapefiles/denmark_poi.shp denmark_poi > denmark.pg/denmark_poi.sql
	shp2pgsql -s 4326:3857 -I denmark.shapefiles/denmark_water.shp denmark_water > denmark.pg/denmark_water.sql

Import into Postgres:

	# On database: create extension postgis;
	psql -d openstreetmap_3857 -h localhost -U postgres -f denmark.pg/denmark_administrative.sql
	psql -d openstreetmap_3857 -h localhost -U postgres -f denmark.pg/denmark_coastline.sql
	psql -d openstreetmap_3857 -h localhost -U postgres -f denmark.pg/denmark_highway.sql
	psql -d openstreetmap_3857 -h localhost -U postgres -f denmark.pg/denmark_location.sql
	psql -d openstreetmap_3857 -h localhost -U postgres -f denmark.pg/denmark_natural.sql
	psql -d openstreetmap_3857 -h localhost -U postgres -f denmark.pg/denmark_poi.sql
	psql -d openstreetmap_3857 -h localhost -U postgres -f denmark.pg/denmark_water.sql
	
Query data:

	psql -d openstreetmap_3857 -h localhost -U postgres -t -c "select gid, type, name, st_astext(geom) from denmark_highway where name<>'' limit 1;"
	
