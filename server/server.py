from pathlib import Path

from bson.objectid import ObjectId
import os
import cherrypy
from jinja2 import Environment, FileSystemLoader
from pymongo import MongoClient

from cherrypy.lib.static import serve_file
import bcrypt

import json
import pickle

from faker import Faker

class AuthenticationModule:
    def __init__(self):
        client = MongoClient(os.environ["MONGODB_URI"])
        self.db = client.survey_db["data"]["authentication"]

    def get_hashed_password(self, plain_text_password):
        # Hash a password for the first time
        #   (Using bcrypt, the salt is saved into the hash itself)
        # copied from https://stackoverflow.com/a/23768422
        return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, plain_text_password, hashed_password):
        # Check hashed password. Using bcrypt, the salt is saved into the hash itself
        # copied from https://stackoverflow.com/a/23768422
        return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)

    def check_password_in_db(self, realm, username, password):
        # signature as specified in https://docs.cherrypy.dev/en/latest/pkg/cherrypy.lib.auth_basic.html
        all_matching_data = [entry for entry in self.db.find({"realm":realm, "username":username})]
        if len(all_matching_data) == 1:
            return self.check_password(password, all_matching_data[0]["password"])
        else:
            return False

class AppServer:
    """
    Serves pages, deals with any APIs
    """
    def __init__(self, realm):
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
        self.db = client.survey_db["victims"]

        self.realm = realm

    def _render_template(self, tmpl_name, params={}):
        """

        :param tmpl_name:
        :param params:
        :return:
        """
        tmpl = self._env.get_template(tmpl_name)
        return tmpl.render(**params)

    @cherrypy.expose
    def index(self, **kwargs):
        """

        :return:
        """
        all_data = self.db.find({})

        if "admin_mode" in kwargs:
            admin_mode = kwargs["admin_mode"]
        else:
            admin_mode = False

        return self._render_template('index.html', params={'title': "Index Page", "data": all_data, "admin_mode": admin_mode})

    @cherrypy.expose
    def upload(self):
        if "LOCAL" in os.environ and os.environ["LOCAL"]:
            return self._render_template("upload.html")
        else:
            return self._render_template("index.html")

    @cherrypy.expose
    def upload_file(self, starting_data):
        if "LOCAL" in os.environ and os.environ["LOCAL"]:
            out_file = Path(__file__).resolve().parents[1].joinpath("static/data/out.json")

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
            save_file = Path(__file__).resolve().parents[1].joinpath("static/data/data.pickle")

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

        return self._render_template('survey.html', params={'title': "Survey", "post_route": f"{self.realm}/POST", "id": id,
                                                            "data" : data,
                                                            **{key : record[key] for key in self.identifying_info},
                                                            **current_data})

    @cherrypy.expose
    def add(self):
        """

        :return:
        """
        return self._render_template('add.html', params={'title': "Add Victim", "post_route": f"{self.realm}/POST_ADD"})

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
        query = {"Nachname": kwargs["Nachname"], "Vorname": kwargs["Vorname"], "URL": kwargs["URL"]}
        existing_records = [entry for entry in self.db.find(
            {"_id": ObjectId(id)})]

        # only should be one entry
        assert(len(existing_records) == 1)

        record = existing_records[0]
        record["data"].append({key : kwargs[key] for key in kwargs.keys() if key not in self.identifying_info})

        self.db.update_one({"_id": ObjectId(id)}, {"$set": {**query, "data": record["data"]}})

        # maybe better to have a landing page for this or new profile shown
        return self.index()

    @cherrypy.expose
    def POST_USER(self, **kwargs):
        if kwargs["username"] == cherrypy.request.login:
            self.enter_credentials_in_db(**kwargs)
            return self.index()
        else:
            raise ValueError("You can only modify the password for your own username!")

    @cherrypy.expose
    def user_administration(self, username=None, admin_mode=False):
        if username is None:
            username = self.random_username()
            return self._render_template("user_administration.html", params={"post_route": f"{self.realm}/POST_USER", "username":username, "password":self.random_password(), "existing": False, "admin_mode":admin_mode})
        else:
            return self._render_template("user_administration.html",
                                         params={"post_route": f"{self.realm}/POST_USER", "username": username,
                                                 "password": self.random_password(), "existing": True, "admin_mode":admin_mode})


class AdminConsole(AppServer):
    def __init__(self, realm):
        """
        Sets up some basic information, like template path and environment.
        """
        super().__init__(realm=realm)

        self.faker = Faker('en_GB')
        self.authentication = AuthenticationModule()
        # self.authentication.db.delete_many({})

        try:
            self.enter_credentials_in_db("admin", "dev", "dev-password")
            self.enter_credentials_in_db("survey", "git", "tester-password")
        except:
            pass

    @cherrypy.expose
    def random_username(self):
        # UK cities to avoid numbering, not use a city where a KZ might be
        current_users = [entry["username"] for entry in self.authentication.db.find({})]
        new_user = f"datenerfasser/in_{self.faker.city().replace(' ', '_')}"

        while new_user in current_users:
            new_user = f"datenerfasser/in_{self.faker.city().replace(' ', '_')}"

        return new_user

    def random_password(self):
        return self.faker.password(length=12)

    @cherrypy.expose
    def POST_USER(self, **kwargs):
        self.enter_credentials_in_db(**kwargs)
        return self.index(admin_mode=True)

    @cherrypy.expose
    def user_administration(self, username=None):
        return super().user_administration(admin_mode=True)

    def enter_credentials_in_db(self, realm, username, password, existing=False):
        # only store hashed and salted passwords
        all_matching_data = [entry for entry in self.authentication.db.find({"username": username})]
        if len(all_matching_data) == 0:
            self.authentication.db.insert_one({"realm": realm, "username": username, "password": self.authentication.get_hashed_password(password)})
        elif existing:
            self.authentication.db.update_one({"username": username}, {"$set": {"realm": realm, "username": username, "password": self.authentication.get_hashed_password(password)}})
        else:
            raise ValueError("Username already is taken!")

    @cherrypy.expose
    def index(self, **kwargs):
        print([entry for entry in self.authentication.db.find({})])
        return super().index(admin_mode=True)

    @cherrypy.expose
    def users(self):
        return self._render_template('users.html', params={"data":[{"username":entry["username"]} for entry in self.authentication.db.find({})]})