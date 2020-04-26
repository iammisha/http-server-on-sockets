import base64
from sqlite_connector import SQLiteAPI
from utils import get_body, parse_parameters, check_credentials


def basic_auth_decorator(view):
    def wrapper(*args, **kwargs):
        headers = kwargs['headers']
        response_body = get_body('index.html')
        if 'Authorization' not in headers:
            return "HTTP/1.1 401 Unauthorized", ['WWW-Authenticate: Basic realm="Log in"'], response_body
        else:
            try:
                credentials = base64.b64decode(headers['Authorization'].split(' ')[1]).decode("utf-8").split(':')
                if not check_credentials(credentials):
                    return "HTTP/1.1 401 Unauthorized", ['WWW-Authenticate: Basic realm="Log in"'], response_body
            except Exception as error:
                return "HTTP/1.1 400 Bad Request", ['WWW-Authenticate: Basic realm="Log in "'], ''
        return view(*args, **kwargs)
    return wrapper


def main(method, querystring, headers, body):
    if method == "GET":
        response_line = 'HTTP/1.1 200 OK'
        response_headers = []
        response_body = get_body('index.html')
        return response_line, response_headers, response_body
    elif method == 'POST':
        parameters = parse_parameters(body)
        username, password = parameters['username'], parameters['password']
        db = SQLiteAPI()
        # todo hash password
        if db.add_user(username, password):
            template = 'successful_registration.html'
        else:
            template = 'unsuccessful_registration.html'

        response_line = 'HTTP/1.1 200 OK'
        response_headers = []
        response_body = get_body(template)
        return response_line, response_headers, response_body
    else:
        response_line = "HTTP/1.1 405 Method Not Allowed"
        response_headers = []
        response_body = get_body('405.html')
        return response_line, response_headers, response_body


@basic_auth_decorator
def timer(method, querystring, headers, body):
    if method == "GET":
        response_line = 'HTTP/1.1 200 OK'
        response_headers = []
        response_body = get_body('timer.html')
        return response_line, response_headers, response_body
    else:
        response_line = "HTTP/1.1 405 Method Not Allowed"
        response_headers = []
        response_body = get_body('405.html')
        return response_line, response_headers, response_body


