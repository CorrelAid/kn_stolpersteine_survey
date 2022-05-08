from pathlib import Path
from bson.objectid import ObjectId
import os
import cherrypy
from jinja2 import Environment, FileSystemLoader
from pymongo import MongoClient
from cherrypy.lib.static import serve_file
import json
import pickle
import authentication_tool


class AppServer:
    """
    Serves pages, deals with any APIs
    """

    def __init__(self):
        """
        Sets up some basic information, like template path and environment.
        """
        self._tmpl_dir = Path(
            __file__).parents[0].resolve().joinpath('templates')
        print(self._tmpl_dir)
        self._env = Environment(loader=FileSystemLoader(self._tmpl_dir))

        self.identifying_info = ["Vorname", "Nachname", "URL"]

        # possibly init other APIs
        # locally, start mongo first: service mongod start
        # client = MongoClient("localhost", 27010)
        client = MongoClient(os.environ["MONGODB_URI"])
        print(client.list_database_names())
        # using collections instead of databases here now i think
        self.db = client.survey["data"]["victims"]
        # self.db.delete_many({})

    def _render_template(self, tmpl_name, params={}):
        """

        :param tmpl_name:
        :param params:
        :return:
        """
        tmpl = self._env.get_template(tmpl_name)
        return tmpl.render(**params)

    @cherrypy.expose
    @authentication_tool.require()
    def index(self):
        """

        :return:
        """
        cherrypy.response.cookie["hallo"] = "world"
        all_data = self.db.find({})
        return self._render_template('index.html', params={'title': "Index Page", "data": all_data})

    @cherrypy.expose
    def upload(self):
        if "LOCAL" in os.environ and os.environ["LOCAL"]:
            return self._render_template("upload.html")
        else:
            return self._render_template("index.html")

    @cherrypy.expose
    def upload_file(self, starting_data):
        if "LOCAL" in os.environ and os.environ["LOCAL"]:
            out_file = Path(__file__).resolve().parents[1].joinpath(
                "static/data/out.json")

            with open(out_file, "wb") as f:
                data = starting_data.file.read()
                f.write(data)

            with open(out_file, "rb") as f:
                entries = json.load(f)
            self.db.insert_many(entries)

    @cherrypy.expose
    def download(self):
        if "LOCAL" in os.environ and os.environ["LOCAL"]:
            all_data = [entry for entry in self.db.find({})]
            print(all_data)
            save_file = Path(__file__).resolve().parents[1].joinpath(
                "static/data/data.pickle")

            with open(save_file, "wb") as f:
                pickle.dump(all_data, f)

            return serve_file(save_file, "application/x-download", "attachment")

    @cherrypy.expose
    def survey(self, id):
        """

        :param vorname:
        :param nachname:
        :param url:
        :return:
        """
        query = {"_id": ObjectId(id)}
        existing_records = [entry for entry in self.db.find(query)]

        # only should be one entry
        assert(len(existing_records) == 1)

        record = existing_records[0]

        # if existing data, take most up-to-date copy
        if len(record["data"]) > 0:
            current_data = record["data"][-1]
        else:
            current_data = {}

        data = self.db.find({})

        return self._render_template('survey.html', params={'title': "Survey", "post_route": "POST", "id": id,
                                                            "data": data,
                                                            **{key: record[key] for key in self.identifying_info},
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
                                     params={'title': f"Added {info['Nachname']}, {info['Vorname']}", "info": info})

    @cherrypy.expose
    def POST_ADD(self, **kwargs):
        """

        :return:
        """
        existing_records = [entry for entry in self.db.find(kwargs)]
        if "" in kwargs.values():
            # TODO could be better to do this in front-end or at least have a landing page
            raise ValueError("All fields must be completed")
        # already in database
        elif len(existing_records) >= 1:
            return self.fail_add(kwargs)
        else:
            # add data, with empty data entry
            self.db.insert_one({**kwargs, "data": []})
            return self.success_add(self.db.find_one(kwargs))

    @cherrypy.expose
    def POST(self, id, **kwargs):
        """

        :return:
        """
        query = {"Nachname": kwargs["Nachname"],
                 "Vorname": kwargs["Vorname"], "URL": kwargs["URL"]}
        existing_records = [entry for entry in self.db.find(
            {"_id": ObjectId(id)})]

        # only should be one entry
        assert(len(existing_records) == 1)

        record = existing_records[0]
        record["data"].append(
            {key: kwargs[key] for key in kwargs.keys() if key not in self.identifying_info})

        self.db.update_one({"_id": ObjectId(id)}, {
                           "$set": {**query, "data": record["data"]}})

        # maybe better to have a landing page for this or new profile shown
        return self.index()
