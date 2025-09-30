import os
import time
import json
import webbrowser
import traceback
import requests
import ssl
from dotenv import load_dotenv
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, quote_plus
from .utilities import *


# Authentication based on code from: https://github.com/isonium/TDAmeritrade-API
class TDAuthenticationDriver:
    def __init__(self, debug=False):
        load_dotenv()
        self.config = get_config()['TD_AMERITRADE']
        self.debug = debug
        self.auth_filename = os.getenv('CREDENTIAL_CACHE_FILE')
        self.tokens = {'access_token': None,
                       'refresh_token': None,
                       }
        self.redirect_uri = "https://" + self.config['HOST']
        if self.config['PORT'] != 443:
            self.redirect_uri = self.redirect_uri + ":" + str(self.config['PORT'])
        self.client_id = self.config['API_KEY'] + "@" + self.config['OAUTH']
        self.redirect_uri_encoded = quote_plus(self.redirect_uri)

        # Check if an authentication cache file exists.
        if os.path.isfile(self.auth_filename):
            try:
                with open(self.auth_filename, "r") as token_fh:
                    self.tokens = json.load(token_fh)
            except:
                pass

    def verify_ssl_reqs(self):
        ret_val = True
        if not os.path.isfile(os.getenv('SSL_CERT_FILE')) or not os.path.isfile(os.getenv('SSL_KEY_FILE')):
            print("")
            print("You need to generate SSL certificates")
            print("")
            print("openssl req -newkey rsa:2048 -nodes -keyout {} -x509 -days 365 -out {}".format(
                os.getenv('SSL_KEY_FILE'),
                os.getenv('SSL_CERT_FILE')))
            print("")
            ret_val = False
        return ret_val

    def write_tokens(self, auth_reply):
        response = json.loads(auth_reply)
        response.setdefault('error', [None])
        if response['error'][0] is None:
            tmp_tokens = json.loads(auth_reply)
            tmp_tokens['grant_time'] = int(time.time())
            access_token_expire = time.time() + int(tmp_tokens['expires_in'])
            refresh_token_expire = time.time() + int(tmp_tokens['refresh_token_expires_in'])
            tmp_tokens['access_token_expires_at'] = access_token_expire
            tmp_tokens['refresh_token_expires_at'] = refresh_token_expire
            tmp_tokens['access_token_expires_at_date'] = datetime.fromtimestamp(access_token_expire).isoformat()
            tmp_tokens['refresh_token_expires_at_date'] = datetime.fromtimestamp(refresh_token_expire).isoformat()
            tmp_tokens['logged_in'] = True

            # Write main auth file
            with open(self.auth_filename, "w") as tmp_file:
                json.dump(tmp_tokens, tmp_file, indent=4)
            print('Tokens updated and written to {}.'.format(self.auth_filename))

    def __update_tokens(self):
        if time.time() > self.tokens['grant_time'] + self.tokens['expires_in'] / 5 * 4:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {'grant_type': 'refresh_token', 'refresh_token': self.tokens['refresh_token'],
                    'access_type': 'offline',
                    'code': '', 'client_id': self.client_id, 'redirect_uri': self.redirect_uri}
            auth_reply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
            self.write_tokens(auth_reply.text)

    def authenticate(self, force=False):
        if not force and self.tokens['access_token'] is not None:
            self.__update_tokens()
        else:
            if self.debug:
                print('OAuth session started. Opening web authentication page...')
            try:
                httpd = HTTPServer((self.config['HOST'], self.config['PORT']), TDAuthenticationHandler)
                httpd.socket = ssl.wrap_socket(httpd.socket, keyfile=os.getenv('SSL_KEY_FILE'),
                                               certfile=os.getenv('SSL_CERT_FILE'), server_side=True)
                webbrowser.open_new(
                    "https://auth.tdameritrade.com/auth?response_type=code&redirect_uri=" + self.redirect_uri_encoded + "&client_id=" + self.client_id)
                httpd.serve_forever()
            except PermissionError:
                print("Unable to bind " + self.config['HOST'] + ":" + str(
                    self.config['PORT']) + " with current permissions. (Try 'sudo ./{}')".format(__file__))
            except FileNotFoundError:
                print('Key and Cert .pem files not found. Check configuration.')
            except SystemExit:
                print("Authentication steps completed.")
            except:
                # If the web authentication doesn't happen, enable debug to see what's happening.
                if self.debug:
                    traceback.print_exc()


class TDAuthenticationHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        td_auth = TDAuthenticationDriver()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        path, _, query_string = self.path.partition('?')
        query = parse_qs(query_string)
        query.setdefault('code', [''])
        code = query['code'][0]

        # Grab the code returned, and make a POST to get refresh token.
        if code != '':
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {'grant_type': 'authorization_code', 'access_type': 'offline', 'code': code,
                    'client_id': td_auth.client_id,
                    'redirect_uri': td_auth.redirect_uri}
            auth_reply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
            td_auth.write_tokens(auth_reply.text)
            self.wfile.write(auth_reply.text.encode())
        exit(0)  # Exit web server after token is written.
