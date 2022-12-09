from pathlib import Path
import os
import cherrypy
from jinja2 import Environment, FileSystemLoader
from pymongo import MongoClient
from .surveys import SurveyObject
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
        all_matching_data = [entry for entry in self.db.find(
            {"realm": realm, "username": username})]
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
        self.faker = Faker('en_GB')
        self._tmpl_dir = Path(
            __file__).parents[0].resolve().joinpath('templates')
        self._env = Environment(loader=FileSystemLoader(self._tmpl_dir))

        self.identifying_info = ["Vorname", "Nachname", "URL"]
        self.authentication = AuthenticationModule()

        # possibly init other APIs
        # locally, start mongo first: service mongod start
        # client = MongoClient("localhost", 27010)
        client = MongoClient(os.environ["MONGODB_URI"])
        self.db = client.survey_db["victims"]

        self.realm = realm

    def _render_template(self, tmpl_name, params=None):
        """

        :param tmpl_name:
        :param params:
        :return:
        """
        if params is None:
            params = {"user": cherrypy.request.login}
        else:
            params = {**params, "user": cherrypy.request.login}
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

        return self._render_template('survey_index.html', params={'title': "Übersicht", "data": all_data, "admin_mode": admin_mode})

    @cherrypy.expose
    def survey(self, _id, admin_mode=False):
        """

        :param vorname:
        :param nachname:
        :param url:
        :return:
        """
        query = {"_id": _id}
        existing_records = [entry for entry in self.db.find(query)]

        # only should be one entry
        assert(len(existing_records) == 1)

        record = existing_records[0]

        data = list(self.db.find({}))

        questions = []
        for question_file in ["add", "survey"]:
            curr_question_file = Path(__file__).resolve().parents[1].joinpath(
                f"static/data/{question_file}.json")
            with open(curr_question_file, "rb") as f:
                questions.extend(json.load(f))

        if not admin_mode:
            # if existing data, take most up-to-date copy
            if len(record["data"]) > 0:
                current_data = record["data"][-1]
            else:
                current_data = {}
            current_data = {**current_data, **{key: record[key] for key in set(record.keys())-set(current_data.keys()) if key != "data"}}

            html = SurveyObject(questions, current_data, data).construct_survey(
                questions, current_data)

            if "URL" in current_data:
                html = f"<h4 class='font-weight-bold pt-2'> Zu übertragen:  <a href='https://www.stolpersteine-konstanz.de/{current_data['URL'] }.html' target='_blank' rel='noopener noreferrer'>https://www.stolpersteine-konstanz.de/{current_data['URL']}.html</a></h4>" + html
        else:
            if len(record["data"]) < 3:
                 return self.fail_admin_overview()
            else:
                html = []
                for name_append, current_data in zip(["second_to_last", "last", ""], record["data"][-3:]):
                    current_data = {
                        **current_data, **{key: val for key, val in record.items() if key != "data"}}

                    so = SurveyObject(questions, current_data,
                                      data, name_append=name_append)

                    if "URL" in current_data and not admin_mode:
                        html.append(
                            f"<h4 class='font-weight-bold'>Zu übertragen:  <a href='https://www.stolpersteine-konstanz.de/{current_data['URL']}.html' target='_blank' rel='noopener noreferrer'>https://www.stolpersteine-konstanz.de/{current_data['URL']}.html</a></h4>" + so.construct_survey(questions, current_data))
                    elif admin_mode:
                        html.append(
                            f"<h4 class='font-weight-bold'>User ID: {current_data['user']}</h4>" + so.construct_survey(
                                questions, current_data))

        return self._render_template('survey.html', params={'title': "Datenerfassung", "post_route": f"{self.realm}/POST",
                                                            "html": html, "admin_mode": admin_mode})
    
    @cherrypy.expose
    def fail_admin_overview(self):
        return self._render_template('fail_admin_overview.html', params={'title': "Noch nicht genügend Einträge, um diese zu vergleichen"})
    
    @cherrypy.expose
    def add(self, admin_mode=False):
        """

        :return:
        """
        if admin_mode:
            question_file = Path(__file__).resolve(
            ).parents[1].joinpath("static/data/add.json")

            with open(question_file, "rb") as f:
                questions = json.load(f)

            html = SurveyObject(questions, {}, {}).construct_survey(questions, {})

            return self._render_template('add.html', params={'title': "Stolperstein einfügen", "html": html, "post_route": f"{self.realm}/POST_ADD"})
        else:
            return self.index()
        
# This can be called also if not admin till now right?
    @cherrypy.expose
    def POST_ADD(self, **kwargs):
        """

        :return:
        """
        def create_id(Vorname, Nachname, Strasse, Hausnummer, URL):
            special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe'}
            return f"{Vorname.replace(' ', '_').translate(special_char_map)}_{Nachname.translate(special_char_map)}_{Strasse[:2].translate(special_char_map)}{Hausnummer}".lower().replace("-", "_")

        existing_records = [entry for entry in self.db.find(kwargs)]
        if "" in kwargs.values():
            return self._render_template('post_add_completeAllFields.html', params={'title': "Alle Felder müssen ausgefüllt werden."})
        # already in database
        elif len(existing_records) >= 1:
            return self.fail_add(kwargs)
        else:
            # add data, with empty data entry
            self.db.insert_one(
                {**kwargs, "_id": create_id(**kwargs), "data": []})
            return self.success_post(self.db.find_one(kwargs))

    @cherrypy.expose
    def POST(self, _id, **kwargs):
        """

        :return:
        """
        if "admin_mode" in kwargs:
            admin_mode = kwargs["admin_mode"]
        else:
            admin_mode = False

        query = {"Nachname": kwargs["Nachname"], "Vorname": kwargs["Vorname"], "URL": kwargs["URL"],
                 "Strasse": kwargs["Strasse"], "Hausnummer": kwargs["Hausnummer"]}
        existing_records = [entry for entry in self.db.find(
            {"_id": _id})]

        # only should be one entry
        assert(len(existing_records) == 1)

        record = existing_records[0]
        updated_data = [individual_record for individual_record in record["data"] if individual_record["user"] != cherrypy.request.login] + [{**{key: kwargs[key] for key in kwargs.keys()
                              if key not in self.identifying_info}, "user": cherrypy.request.login}]

        self.db.update_one(
            {"_id": _id}, {"$set": {**query, "fertig": admin_mode, "data": updated_data}})


        # maybe better to have a landing page for this or new profile shown
        return self.success_add(self.db.find_one({"_id": _id}))

    @cherrypy.expose
    def POST_USER(self, **kwargs):
        if kwargs["username"] == cherrypy.request.login:
            self.enter_credentials_in_db("survey", **kwargs)
            return self.index()
        else:
            raise ValueError(
                "You can only modify the password for your own username!")

    def random_password(self):
        return self.faker.password(length=12)

    @cherrypy.expose
    def user_administration(self, username=None, admin_mode=False):
        if username in [entry["username"] for entry in self.authentication.db.find({"realm": "admin"})]:
            realm = "admin"
        else:
            realm = "survey"
        return self._render_template("user_administration.html",
                                     params={"post_route": f"{self.realm}/POST_USER", "realm": realm,
                                             "username": username if username else cherrypy.request.login,
                                             "password": self.random_password(), "existing": True, "admin_mode": admin_mode, "title": "Accounteinstellungen"})

    def enter_credentials_in_db(self, realm, username, password, existing=False):
        # only store hashed and salted passwords
        all_matching_data = [
            entry for entry in self.authentication.db.find({"username": username})]
        if len(all_matching_data) == 0:
            self.authentication.db.insert_one(
                {"realm": realm, "username": username, "password": self.authentication.get_hashed_password(password)})
        elif existing:
            self.authentication.db.update_one({"username": username}, {"$set": {
                                              "realm": realm, "username": username, "password": self.authentication.get_hashed_password(password)}})
        else:
            raise ValueError("Username already is taken!")
        
    
    # @cherrypy.expose
    # def delete_entries(self):
    #     # TODO This is only here for testing, this must be removed just in case!!
    #     length_all_data = len(list(self.db.find({})))
    #     self.db.delete_many({})
    #     return self.success_delete(length_all_data)
    
    ### custom error messages ###########################
    #####################################################
    
    @cherrypy.expose
    def fail_add(self, info):
        """

        :return:
        """
        return self._render_template('fail_add.html', params={'title': "Stolperstein schon in der Datenbank.", "info": info})

    @cherrypy.expose
    def success_add(self, info):
        """

        :return:
        """
        return self._render_template('success_add.html',
                                     params={'title': f" {info['Nachname']}, {info['Vorname']} hinzugefügt."})

    def success_post(self, info):
        """

        :return:
        """
        return self._render_template('success_add.html',
                                     params={'title': f" {info['Nachname']}, {info['Vorname']} bearbeitet."})

    @cherrypy.expose
    def success_delete(self, num_entries):
        """

        :return:
        """
        return self._render_template('success_delete.html',
                                     params={'title': f"{num_entries} Einträge gelöscht.", "num_entries": num_entries})

    @cherrypy.expose
    def success_upload(self, num_entries):
        """

        :return:
        """
        return self._render_template('success_upload.html',
                                     params={'title': f"{num_entries} Einträge hochgeladen.", "num_entries": num_entries})


class AdminConsole(AppServer):
    def __init__(self, realm):
        """
        Sets up some basic information, like template path and environment.
        """
        super().__init__(realm=realm)

        # self.authentication.db.delete_many({})

        try:
            self.enter_credentials_in_db(
                "admin", os.environ['USERNAME'], os.environ['PASSWORD'], False)
        except:
            pass

    @cherrypy.expose
    def POST_USER(self, **kwargs):
        self.enter_credentials_in_db(**kwargs)
        return self.users()

    @cherrypy.expose
    def random_username(self):
        # UK cities to avoid numbering, not use a city where a KZ might be
        current_users = [entry["username"]
                         for entry in self.authentication.db.find({})]
        new_user = f"datenerfasser/in_{self.faker.city().replace(' ', '_')}"

        while new_user in current_users:
            new_user = f"datenerfasser/in_{self.faker.city().replace(' ', '_')}"

        return new_user

    @cherrypy.expose
    def user_administration(self, username=None, admin_mode=True):
        if username is None:
            username = self.random_username()
            return self._render_template("user_administration.html",
                                         params={"post_route": f"{self.realm}/POST_USER", "realm": "survey",
                                                 "username": username, "password": self.random_password(),
                                                 "existing": False, "admin_mode": admin_mode, "title": "Accounteinstellungen"})
        else:
            return super().user_administration(username=username, admin_mode=admin_mode)

    @cherrypy.expose
    def index(self, **kwargs):
        return super().index(admin_mode=True)

    @cherrypy.expose
    def survey(self, _id):
        return super().survey(_id, admin_mode=True)

    @cherrypy.expose
    def add(self):
        return super().add(admin_mode=True)

    @cherrypy.expose
    def users(self):
        return self._render_template('users.html', params={"data": [{"username": entry["username"]} for entry in self.authentication.db.find({})]})

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
            return self.success_upload(len(entries))

    @cherrypy.expose
    def POST(self, _id, **kwargs):
        return super().POST(_id, admin_mode=True, **kwargs)

    @cherrypy.expose
    def download(self):
        if "LOCAL" in os.environ and os.environ["LOCAL"]:
            all_data = [entry for entry in self.db.find({})]

            # not true anymore I (Jonas) think (works)
            # remove object _id since not json serializable
            # all_data = [{key: val for key, val in victim_data.items() if key != "_id"}
            #             for victim_data in all_data]

            save_file = Path(__file__).resolve(
            ).parents[1].joinpath("static/data/out.json")

            # https://stackoverflow.com/q/3503102
            with open(save_file, "w") as f:
                json.dump(all_data, f)

            return serve_file(save_file, "application/x-download", "attachment")

    

class Public:
    def __init__(self):
        """
        Sets up some basic information, like template path and environment.
        """
        self._tmpl_dir = Path(
            __file__).parents[0].resolve().joinpath('templates')
        self._env = Environment(loader=FileSystemLoader(self._tmpl_dir))

    def _render_template(self, tmpl_name, params={}):
        """

        :param tmpl_name:
        :param params:
        :return:
        """
        tmpl = self._env.get_template(tmpl_name)
        return tmpl.render(**params)
    
    @cherrypy.expose
    def instructions(self, **kwargs):

        return self._render_template('instructions.html', params={'title': "Anleitung"})
    
        
    @cherrypy.expose
    def logged_out(self):
        return self._render_template('logged_out.html', params={'title': "Ausgeloggt"})
    
    @cherrypy.expose
    def index(self):
        return self._render_template('index.html', params={'title': "Index"})
    
    @cherrypy.expose
    def Impressum(self):
        return self._render_template('impressum.html', params={'title': "Impressum"})
    
    