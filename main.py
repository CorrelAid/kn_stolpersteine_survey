from pathlib import Path
import os

import cherrypy
from server import AppServer, AuthenticationModule, AdminConsole, Public
from dotenv import load_dotenv

if __name__ == '__main__':
    if "PORT" not in os.environ:
        load_dotenv(Path(__file__).resolve().parents[0].joinpath(".env"))

    PATH = os.path.abspath(os.path.dirname(__file__))

    class Root:
        pass

    def error_page_401(status, message, traceback, version):
        return "Sie sind nicht berechtigt, auf diese Seite zuzugreifen."

    cherrypy.config.update({'error_page.401': error_page_401})

    LOCAL = os.environ.get("LOCAL")

    # if LOCAL:
    #     cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    # else:
    #     cherrypy.config.update({'server.socket_host': ''})

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': int(os.environ['PORT']),
        'tools.sessions.on': True,
        # sessions will be saved in RAM since next two lines are commented out
        # 'tools.sessions.storage_type': "File",
        # 'tools.sessions.storage_path': 'sessions',
        'tools.sessions.timeout': 1})

    cherrypy.tree.mount(AppServer("survey"), '/survey', config={
        '/': {
            'tools.auth_basic.on': True,
            'tools.auth_basic.realm': 'survey',
            'tools.auth_basic.checkpassword': AuthenticationModule().check_password_in_db}})

    cherrypy.tree.mount(AdminConsole("admin"), '/admin',  config={
        '/': {
            'tools.auth_basic.on': True,
            'tools.auth_basic.realm': 'admin',
            'tools.auth_basic.checkpassword': AuthenticationModule().check_password_in_db,
            'tools.auth_basic.accept_charset': 'UTF-8'}})

    cherrypy.tree.mount(Public(), '/', config={
        "/":{
            "tools.staticdir.root": PATH,},
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': "static",

        }})

    cherrypy.engine.start()
    cherrypy.engine.block()
