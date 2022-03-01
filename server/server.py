from pathlib import Path

import os
import cherrypy
from jinja2 import Environment, FileSystemLoader
from pymongo import MongoClient


class AppServer:
    """
    Serves pages, deals with any APIs
    """

    def __init__(self):
        """
        Sets up some basic information, like template path and environment.
        """
        self._tmpl_dir = Path(__file__).parents[0].resolve().joinpath('templates')
        print(self._tmpl_dir)
        self._env = Environment(loader=FileSystemLoader(self._tmpl_dir))

        # possibly init other APIs
        # locally, start mongo first: service mongod start
        # client = MongoClient("localhost", 27010)
        client = MongoClient(os.environ["MONGODB_URI"])
        print(client.list_database_names())
        self.db = client["data"]["victims"]

        # # example entry to start with
        # example_entries = [{"vorname": "Emma", "nachname": "Adler", "url": "adler_emma", "data": []},
        #                    {"vorname": "Margarete", "nachname": "DURST", "url": "durst_margarete",
        #                     "data": [{"geburtsname": "Halbach",
        #                               "opfergruppen": ["juedisch"],
        #                               "geburtsjahr": 1905}]}]
        #
        # self.db.insert_many(example_entries)

    def _render_template(self, tmpl_name, params={}):
        """

        :param tmpl_name:
        :param params:
        :return:
        """
        tmpl = self._env.get_template(tmpl_name)
        return tmpl.render(**params)

    @cherrypy.expose
    def index(self):
        """

        :return:
        """
        data = self.db.find({})
        return self._render_template('index.html', params={'title': "Index Page", "data": data})

    @cherrypy.expose
    def survey(self, vorname, nachname, url):
        """

        :param vorname:
        :param nachname:
        :param url:
        :return:
        """
        identifying_info = {"vorname": vorname, "nachname": nachname, "url": url}
        res = [entry for entry in self.db.find(identifying_info)]

        # if existing data, take most up-to-date copy
        if len(res[0]["data"])>0:
            current_data=res[0]["data"][-1]
        else:
            current_data={}

        return self._render_template('survey.html', params={'title': "Survey", "post_route": "POST", **identifying_info,
                                                            **current_data})

    @cherrypy.expose
    def add(self):
        """

        :return:
        """
        return self._render_template('add.html', params={'title': "Add Victim", "post_route": "POST_ADD"})

    @cherrypy.expose
    def fail_add(self, info):
        """

        :return:
        """
        return self._render_template('fail_add.html', params={'title': "Victim Already in Database", "info": info})

    @cherrypy.expose
    def success_add(self, info):
        """

        :return:
        """
        return self._render_template('success_add.html',
                                     params={'title': f"Added {info['nachname']}, {info['vorname']}", "info": info})

    @cherrypy.expose
    def POST_ADD(self, **kwargs):
        """

        :return:
        """
        print(kwargs)
        existing_records = [entry for entry in self.db.find(kwargs)]
        if "" in kwargs.values():
            # TODO could be better to do this in front-end or at least have a landing page
            raise ValueError("All fields must be completed")
        # already in database
        elif len(existing_records) >= 1:
            return self.fail_add(kwargs)
        else:
            # add data, with empty data entry
            self.db.insert_one({**kwargs, "data":[]})
            return self.success_add(kwargs)

    @cherrypy.expose
    def POST(self, vorname, nachname, url, **kwargs):
        """

        :return:
        """
        res = [entry for entry in self.db.find({"nachname": nachname, "vorname": vorname, "url": url})]
        if len(res) > 0:
            res = res[0]
            res["data"].append(kwargs)
            self.db.update(res)
        else:
            # this should only happen if incorrect identifying info
            # might be better to handle this by getting identifying info before POST and comparing
            self.db.insert_one({"nachname": nachname, "vorname": vorname, "url": url, "data": [kwargs]})
        # maybe better to have a landing page for this or new profile shown
        return self.index()
