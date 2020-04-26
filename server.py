import socket
import threading
import ssl
import argparse
from views import *
from sqlite_connector import SQLiteAPI
from utils import get_body

parser = argparse.ArgumentParser(description='Parser')
arg_host = parser.add_argument('-H', '--host', dest='host', default='127.0.0.1')
arg_port = parser.add_argument('-p', '--port', dest='port', default=8888, type=int)
args = parser.parse_args()


class ThreadingHttpServer:
    urls = {
        '/': main,
        '/timer': timer,
    }

    def __init__(self, host=socket.gethostbyname(socket.gethostname()), port=8888):
        self.db = SQLiteAPI()
        self.db.create_all_tables()
        self.host = host
        # self.host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # todo ssl
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen()

    @staticmethod
    def parsing_request(data):
        request_line_and_headers, body = data.split('\r\n\r\n')
        parsed = request_line_and_headers.split('\r\n')
        request_line = parsed[0]
        headers = parsed[1:] if len(parsed) > 1 else []
        return request_line, headers, body

    @staticmethod
    def parse_request_line(request_line):
        parsed = request_line.split(' ')
        method = parsed[0]
        url = parsed[1]
        version = parsed[2]
        return method, url, version

    @staticmethod
    def parse_url_and_querystring(url_and_querystring):
        parsed = url_and_querystring.split('?')
        url = parsed[0]
        querystring = '?'.join(parsed[1:]) if len(parsed) > 1 else ''
        return url, querystring

    @staticmethod
    def headers_to_dict(headers):
        headers_dict = dict()
        for header in headers:
            h = header.split(': ')
            if len(h) > 1 and h[0]:
                headers_dict.update({h[0]: ': '.join(h[1:])})
            else:
                raise ValueError
        return headers_dict

    @staticmethod
    def headers_from_dict(headers_dict):
        # todo
        headers = list()
        return headers_dict

    def _generate_response(self, data):
        try:
            request_line, headers, body = self.parsing_request(data)
            method, url_and_querystring, version = self.parse_request_line(request_line)
            url, querystring = self.parse_url_and_querystring(url_and_querystring)
            headers = self.headers_to_dict(headers)
            if not version == "HTTP/1.1":
                headers_response = []
                body_response = ''
                return "HTTP/1.1 505 HTTP Version Not Supported", headers_response, body_response
            if url not in self.urls:
                headers_response = []
                body_response = get_body('404.html')
                return "HTTP/1.1 404 Not Found", headers_response, body_response

        except ValueError:
            headers_response = []
            body_response = ''
            return 'HTTP/1.1 400 Bad Request', headers_response, body_response
        return self.urls[url](method=method, querystring=querystring, headers=headers, body=body)

    def connection_handler(self, client_connection):
        request = client_connection.recv(1024).decode()
        response_line, response_headers, response_body = self._generate_response(request)
        response = '{}\r\n{}\r\n\r\n{}'.format(response_line, '\r\n'.join(response_headers), response_body)
        client_connection.sendall(bytes(response, "utf8"))
        client_connection.close()

    def run(self):
        while True:
            client_connection, client_addr = self.sock.accept()
            conn_thread = threading.Thread(target=self.connection_handler, args=(client_connection, ))
            conn_thread.daemon = True
            conn_thread.start()


if __name__ == "__main__":
    server = ThreadingHttpServer(args.host, args.port)
    print("{}:{}".format(args.host, args.port))
    server.run()








