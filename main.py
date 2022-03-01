from pathlib import Path

import os
import cherrypy
from server import AppServer

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ['PORT']),
    })

    cherrypy.tree.mount(AppServer(), '/', {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': Path(__file__).parents[0].resolve().joinpath('static')
        }
    })

    cherrypy.engine.start()
    cherrypy.engine.block()
