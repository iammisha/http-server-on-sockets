from sqlite_connector import SQLiteAPI

TEMPLATES = 'templates/'


def get_body(file):
    with open(TEMPLATES + file) as template:
        response_body = template.read()
    return response_body


def parse_parameters(data):
    try:
        parameters = data.split('&')
        parameters = dict(tuple(d.split('=')) for d in parameters)
        return parameters
    except:
        return dict()


def check_credentials(credentials=None):
    user = credentials[0]
    password = credentials[1]
    db = SQLiteAPI()
    if db.check_user(user, password):
        return True
    return False
