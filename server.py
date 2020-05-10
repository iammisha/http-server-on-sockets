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
    def parsing_request(http):
        request_line, *headers, _, body = http.split('\r\n')
        return request_line, headers, body

    @staticmethod
    def parse_request_line(request_line):
        method, url_and_querystring, version = request_line.split(' ')
        return method, url_and_querystring, version

    @staticmethod
    def parse_url_and_querystring(url_and_querystring):
        url, *querystring = url_and_querystring.split('?', maxsplit=1)
        querystring = ''.join(querystring)
        return url, querystring

    @staticmethod
    def headers_to_dict(headers):
        headers_dict = dict(line.split(': ', maxsplit=1) for line in headers)
        return headers_dict

    @staticmethod
    def headers_from_dict(headers_dict):
        # todo
        headers = list()
        return headers_dict

    def _generate_response(self, http_request):
        try:
            request_line, headers, body = self.parsing_request(http_request)
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
        http_request = client_connection.recv(1024).decode()
        response_line, response_headers, response_body = self._generate_response(http_request)
        # process_response(response)
        response = '{}\r\n{}\r\n\r\n{}'.format(response_line, '\r\n'.join(response_headers), response_body)
        client_connection.sendall(bytes(response, "utf8"))
        client_connection.close()

    # @staticmethod
    # def process_response(response):
    #     return (
    #         'HTTP/1.1 200\r\n'
    #         f'Content-Length: {len(response)}\r\n'
    #         'Content-Type: text/html\r\n'
    #         '\r\n'
    #         f'{response}'
    #         '\r\n'
    #     )

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








