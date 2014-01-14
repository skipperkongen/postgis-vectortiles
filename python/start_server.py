#!/usr/bin/env python2.7
import os

from tornado.options import define, options, parse_command_line

from pgtiler.web import TornadoServer

define("port", default=8080, help="run on the given port", type=int)

if __name__ == '__main__':
    parse_command_line()
    static_path = os.path.join(os.path.dirname(__file__), "static")
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    configuration_path = os.path.join(os.path.dirname(__file__), "conf")

    TornadoServer(
        port=options.port,
        static_path=static_path,
        template_path=template_path,
        configuration_path=configuration_path
    )

