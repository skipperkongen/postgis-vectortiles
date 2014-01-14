# PGTiler

This directory contains the pg_tiler server (python directory), and a pg_tiler HTML demo configured to match the
server configuration.

## PGTiler server
The PGTiler server is contained in the directory './python'.

Start the server by running the script './python/start_server.py':

```
/python/start_server.py
```

The server is configured to connect to a PostgreSQL database called 'cvl_paper' on localhost and serve data from a table
'denmark_highway' containing openstreetmap streets for Denmark. After you have started the server, you can try the
following requests:

Get an index-tile from the server:

```
curl http://localhost:8080/vectile/denmark_highway/3857/18/140231/82057.ids
```

Get a vector-tile from the server:

```
curl http://localhost:8080/vectile/denmark_highway/3857/18/140231/82057.json
```

See the file ./python/conf/datasources.conf for the datasource configuation of this server. The other configuration-file
in this directory is ./python/conf/cluster.conf. It contains IP addresses for memcached nodes that will be used be
the PGTiler server to cache vector tiles.

## PGTiler HTML demo

The HTML demo is contained in the directory './html'.

Simply open the following file in a browser after you have started the server.

* ./html/vectile.html


