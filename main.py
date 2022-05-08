from pathlib import Path
import os

import cherrypy
from server import AppServer
from dotenv import load_dotenv



if __name__ == '__main__':
    if "PORT" not in os.environ:
        load_dotenv(Path(__file__).resolve().parents[0].joinpath(".env"))

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ['PORT']),
        'tools.zkauth.on': True,
        'tools.sessions.on': True,
        'tools.sessions.name': 'zknsrv'

    })

    cherrypy.tree.mount(AppServer(), '/', {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': Path(__file__).parents[0].resolve().joinpath('static')
        }
    })

    cherrypy.engine.start()
    cherrypy.engine.block()
