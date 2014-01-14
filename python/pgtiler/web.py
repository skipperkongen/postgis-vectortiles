import os
import ConfigParser
import time
import datetime
import traceback
import json
import geojson
import uuid

import memcache

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from postgis import PGSource, PGConnectionSettings
from gridsets import gridset_by_srid
from maprules import ResolutionRule

# http://localhost:8080/vectile/denmark_highway/3857/17/70123/41032.ids


class TornadoServer(object):
    """docstring for TornadoBase"""

    def __init__(self, port=8080, static_path=None, template_path=None, configuration_path=None):
        """

        :param port:
        :param static_path:
        :param template_path:
        :param configuration_path:
        """
        super(TornadoServer, self).__init__()

        settings = {
            "static_path": static_path,
            "template_path": template_path
        }

        # Read general vectile etc, i.e. caching options
        server_config = ConfigParser.ConfigParser()
        server_config.read(os.path.join(configuration_path, "memcached.conf"))
        memcached_nodes = map(lambda x: x.strip(), server_config.get('memcached', 'nodes').split(","))
        print "Remember to start up memcached nodes (e.g. /usr/bin/memcached): %s" % str(memcached_nodes)
        # Generate a cachekey unique to this server process
        cache_key_formatstring = "vectile_%s:{0}:{1}:{2}:{3}" % uuid.uuid4().hex
        # Pass the following dict to VectileHandler
        caching = {
            'generate_key': (
                lambda dataset, srid, tilekey, extension: cache_key_formatstring.format(dataset, srid, tilekey,
                                                                                        extension)),
            'memcached': memcache.Client(memcached_nodes, debug=0)  # remember to start memcached, /usr/bin/memcached
        }

        # Read postgis datasources etc
        config = ConfigParser.ConfigParser()
        config.read(os.path.join(configuration_path, "datasources.conf"))
        datasources = {}
        for section in config.sections():
            print "[Info] Reading datasource section", section
            connection_settings = PGConnectionSettings(
                db_name=config.get(section, 'db_name'),
                db_host=config.get(section, 'db_host'),
                db_user=config.get(section, 'db_user'),
                db_password=config.get(section, 'db_password')
            )
            ds_name = config.get(section, 'table')
            # Load map rules if exists

            maprules = []
            try:
                maprules_file = config.get(section, 'maprules_file')
                fp = open(os.path.join(configuration_path, "rules", maprules_file), 'r')
                maprules_json = json.load(fp)
                print "[Info] Reading map rules from file", maprules_file
                for rule_json in maprules_json['rules']:
                    maprules.append(
                        ResolutionRule.get_rule(rule_json["where_clause"], **rule_json["args"])
                    )
            except Exception, e:
                print "[Warning] %s" % e

            # Add datasource
            datasources[ds_name] = PGSource(
                connection_settings=connection_settings,
                maprules=maprules,
                table=config.get(section, 'table'),
                fid_col=config.get(section, 'fid_col'),
                geom_col=config.get(section, 'geom_col'),
                property_cols=filter(lambda x: x != '', config.get(section, 'property_cols').split(","))
            )

        # register startup time for built-in uptime handler
        startup_millis = time.mktime(time.gmtime())
        handlers = [
            (r'/', RootHandler),
            (r'/uptime', UptimeHandler, dict([('startup_millis', startup_millis)])),
            (r'/vectile/([a-zA-Z0-9-_]+)/([0-9]+)/([0-9]+)/([0-9]+)/([0-9]+).(json|ids)', PgtilerHandler,
             dict([
                 ('datasources', datasources),
                 ('caching', caching)
             ])),
            (r'/styles/([a-zA-Z0-9-_]+)/([a-zA-Z0-9-_]+).css', MapStyleHandler,
             dict([
                 ('stylesheets_path', os.path.join(static_path, "styles"))
             ]))
        ]

        app = tornado.web.Application(
            handlers, **settings
        )

        http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
        http_server.listen(port)
        print "Starting vectile server on port {0:d}".format(port)
        print "Check demo: demo/vectile.html (open file in browser)"
        print "Try this request: http://localhost:8080/vectile/denmark_highway/3857/18/140231/82057.json"
        print "Also try this request: http://localhost:8080/vectile/denmark_highway/3857/18/140231/82057.ids"

        tornado.ioloop.IOLoop.instance().start()


class MapStyleHandler(tornado.web.RequestHandler):
    def initialize(self, stylesheets_path):
        self.stylesheets_path = stylesheets_path

    def get(self, dataset, stylename):
        fn = os.path.join(self.stylesheets_path, dataset, "{0}.css".format(stylename))
        fh = open(fn, 'r')
        self.set_header('Content-Type', 'text/css; charset=utf-8')
        self.write(fh.read())


class PgtilerHandler(tornado.web.RequestHandler):
    def initialize(self, datasources, caching):
        self.datasources = datasources
        self.caching = caching

    def get(self, dataset, srid, z, x, y, extension):

        try:
            gridset = gridset_by_srid(srid)
            bbox, resolution = gridset.get_bbox(z=int(z), x=int(x), y=int(y), tile_pixel_dims=(256, 256))
            ds = self.datasources[dataset]

            # caching
            tile_id = "z{0}x{1}y{2}".format(z, x, y)
            memcached = self.caching['memcached']

            # Case 1: get features
            if extension == 'json':

                # try cache first
                cachekey = self.caching['generate_key'](dataset, srid, tile_id, extension)
                cached_value = memcached.get(cachekey)
                if cached_value:
                    # set result to cached value
                    result = cached_value
                else:
                    # get result from database
                    features = ds.get_features(bbox, srid, resolution)
                    result = geojson.dumps(geojson.FeatureCollection(features=features))
                    # store result in memcached for future use
                    memcached.set(cachekey, result)
                self.set_status(200)
            # Case 2: get ids
            elif extension == 'ids':
                result = geojson.dumps(geojson.FeatureCollection(ds.get_feature_ids(bbox, srid)))
                self.set_status(200)
            # Case 3: Error
            else:
                result = json.dumps({'error': 'Unknown extension: %s' % extension})
                self.set_status(400)
        except:
            # Case 4: Handle exceptions
            # TODO: Remove...only show stacktrace for demo
            result = json.dumps({'error': 'Trace: %s' % traceback.format_exc()})
            self.set_status(400)

        self.set_header('Access-Control-Allow-Origin', '*')
        #self.set_header('Content-Type','application/json; charset=utf-8')
        self.write(result)
        self.finish()


class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class UptimeHandler(tornado.web.RequestHandler):
    def initialize(self, startup_millis):
        self.startup_millis = startup_millis

    def get(self):
        current_millis = time.mktime(time.gmtime())
        diff_millis = current_millis - self.startup_millis
        delta = datetime.timedelta(seconds=diff_millis)
        self.write("uptime: %dd%ds" % (delta.days, delta.seconds))