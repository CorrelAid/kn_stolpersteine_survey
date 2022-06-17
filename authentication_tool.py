import base64
import logging as log
import re
import cherrypy

#####################################################################
## Code taken from https://me.micahrl.com/blog/cherrypy-cookies-http-basic-authentication/ ##
SESSION_KEY = '_zkn_username'

def protect(*args, **kwargs):
    log.debug("Inside protect()...")

    authenticated = False
    conditions = cherrypy.request.config.get('auth.require', None)
    log.debug("conditions: {}".format(conditions))
    if conditions is not None:
        # A condition is just a callable that returns true or false
        try:
            this_session = cherrypy.session[SESSION_KEY]
            cherrypy.session.regenerate()
            email = cherrypy.request.login = cherrypy.session[SESSION_KEY]
            authenticated = True
            log.debug("Authenticated with session: {}, for user: {}".format(
                    this_session, email))

        except KeyError:
            # If the session isn't set, it either wasn't present or wasn't
            # valid. Now check if the request includes an HTTPBA header like
            # "AUTHORIZATION: Basic <base64shit>"

            authheader = cherrypy.request.headers.get('AUTHORIZATION')
            if authheader:
                b64data = re.sub("Basic ", "", authheader)
                decodeddata = base64.b64decode(b64data.encode("ASCII"))
                email,passphrase = decodeddata.decode().split(":", 1)
                if user_verify(email, passphrase):
                    cherrypy.session.regenerate()
                    cherrypy.session[SESSION_KEY] = cherrypy.request.login = email
                    authenticated = True
                else:
                    log.debug(
                        "Attempted login as '{}', but failed".format(email))
            else:
                log.debug("Auth header was not present.")

        except:
            log.debug(
                "Client has no valid session and did not provide HTTPBA creds")

        if authenticated:
            for condition in conditions:
                if not condition():
                    log.debug(
                        "Authentication succeeded but authorization failed.")
                    raise cherrypy.HTTPError("403 Forbidden")
        else:
            raise cherrypy.HTTPError("401 Unauthorized")

# This could be called cherrypy.tools.ANYTHING; I chose 'zkauth' based on the
# name of my app. Take care NOT to call it 'auth' or the name of any other
# built-in tool.
cherrypy.tools.zkauth = cherrypy.Tool('before_handler', protect)

def require(*conditions):
    """A decorator that appends conditions to the auth.require config var"""
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.require' not in f._cp_config:
            f._cp_config['auth.require'] = []
        f._cp_config['auth.require'].extend(conditions)
        return f
    return decorate

#### CONDITIONS
#
# Conditions are callables that return True
# if the user fulfills the conditions they define, False otherwise
#
# They can access the current user as cherrypy.request.login

# TODO: test this function with cookies, I want to make sure that
#       cherrypy.request.login is set properly so that this function can use
#       it.
def zkn_admin():
    return lambda: user_is_admin(cherrypy.request.login)

def user_is(reqd_email):
    return lambda: reqd_email == cherrypy.request.login

def logout():
    email = cherrypy.session.get(SESSION_KEY, None)
    cherrypy.session[SESSION_KEY] = cherrypy.request.login = None
    return "Logout successful"
#####################################################################
#####################################################################