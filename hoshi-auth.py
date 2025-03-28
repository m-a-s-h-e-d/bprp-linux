import os
import requests
import sys
import webbrowser

from base64 import urlsafe_b64encode
from hashlib import sha256
from secrets import token_bytes
from urllib.parse import urlparse, urljoin, urlencode, parse_qs

# ------------- CONSTANTS ------------- #

HOME_DIRECTORY = os.path.expanduser('~')
DESKTOP_ENTRY_DIRECTORY = '.local/share/applications/'
DESKTOP_ENTRY_FILENAME = 'hoshi-auth.desktop'
PLACEHOLDER = '[REPLACE_WITH_SCRIPT_PATH]'
VERIFIER_FILENAME = 'verifier.temp'
AUTH_FILENAME = 'auth.txt'

BASE_URI = 'https://auth.playbprp.com/'
AUTH_ENDPOINT = '/oidc/auth'
TOKEN_ENDPOINT = '/oidc/token'
RESOURCE = 'https://game.playbprp.com/'
REDIRECT_URI = 'hoshi://auth/finish'
REQUEST_SCOPE = 'offline_access game_session game_master'
MIN_SCOPE = 'game_session'
CLIENT_ID = '1xj41buuyw0wym8c1ca8k'

# ------------- CONSTANTS ------------- #

def print_header():
  header = '''
  ██████████████████████████████████████████████████████████████████████████

  ██╗  ██╗ ██████╗ ███████╗██╗  ██╗██╗     █████╗ ██╗   ██╗████████╗██╗  ██╗
  ██║  ██║██╔═══██╗██╔════╝██║  ██║██║    ██╔══██╗██║   ██║╚══██╔══╝██║  ██║
  ███████║██║   ██║███████╗███████║██║    ███████║██║   ██║   ██║   ███████║
  ██╔══██║██║   ██║╚════██║██╔══██║██║    ██╔══██║██║   ██║   ██║   ██╔══██║
  ██║  ██║╚██████╔╝███████║██║  ██║██║    ██║  ██║╚██████╔╝   ██║   ██║  ██║
  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝    ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝

  ██████████████████████████████████████████████████████████████████████████
  '''
  print(header)


def copy_file_to_destination(file_name, destination_dir):
  try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(current_dir, file_name)
    destination_path = os.path.join(destination_dir, file_name)

    if not os.path.exists(destination_dir):
      os.makedirs(destination_dir)

    with open(source_path, 'r') as file:
      file_content = file.read()

    modified_content = file_content.replace(PLACEHOLDER, __file__)

    with open(destination_path, 'w') as file:
      file.write(modified_content)

    print(f'Successfully generated new desktop entry to handle custom protocol')
  
  except FileNotFoundError:
    print(f'Error: Missing {file_name} in the source path "{current_dir}"')
  
  except Exception as e:
    print(f'Unhandled exception: {e}')


def setup_desktop_entry():
  desktop_entry_dir = os.path.join(HOME_DIRECTORY, DESKTOP_ENTRY_DIRECTORY)
  desktop_entry_path = os.path.join(desktop_entry_dir, DESKTOP_ENTRY_FILENAME)
  copy_file_to_destination(DESKTOP_ENTRY_FILENAME, desktop_entry_dir)
  os.system(f'update-desktop-database {desktop_entry_dir}')
  os.system(f'xdg-mime default hoshi-auth.desktop x-scheme-handler/hoshi;')


def generate_verifier():
  data = token_bytes(24)
  verifier = data.hex().upper()
  
  return verifier


def generate_challenge(verifier):
  hash_obj = sha256(verifier.encode('utf-8'))
  hash_bytes = hash_obj.digest()
  challenge = urlsafe_b64encode(hash_bytes).decode('utf-8').rstrip('=')

  return challenge


def build_login_uri(verifier):
  uri = urljoin(BASE_URI, AUTH_ENDPOINT)
  code_challenge = generate_challenge(verifier)
  params = {
    'client_id': CLIENT_ID,
    'response_type': 'code',
    'scope': REQUEST_SCOPE,
    'resource': RESOURCE,
    'prompt': 'login consent',
    'redirect_uri': REDIRECT_URI,
    'code_challenge': code_challenge,
    'code_challenge_method': 'S256'
  }
  login_uri = f'{uri}?{urlencode(params)}'

  return login_uri


def open_login(verifier):
  login_uri = build_login_uri(verifier)
  webbrowser.open(login_uri)


def cache_verifier(verifier):
  current_dir = os.path.dirname(os.path.abspath(__file__))
  cache_path = os.path.join(current_dir, VERIFIER_FILENAME)
  
  with open(cache_path, 'w') as file:
    file.write(verifier)

def retrieve_verifier():
  current_dir = os.path.dirname(os.path.abspath(__file__))
  cache_path = os.path.join(current_dir, VERIFIER_FILENAME)
  
  try:
    with open(cache_path, 'r') as file:
      verifier = file.read()

    os.remove(cache_path)
    
    return verifier
  
  except FileNotFoundError:
    print(f'Error: Missing {VERIFIER_FILENAME} in the source path "{current_dir}"')
    

def authenticate():
  verifier = generate_verifier()
  cache_verifier(verifier)
  open_login(verifier)

  input('Please authorize the application in your browser. Press Enter after authorizing.')


def parse_uri(uri):
  parsed_uri = urlparse(uri)
  query_params = parse_qs(parsed_uri.query)

  return query_params


def encoded_post(uri, data, headers=None):
  try:
    encoded_data = urlencode(data)
    
    if headers:
      response = requests.post(uri, data=encoded_data, headers=headers)

    else:
      response = requests.post(uri, data=encoded_data)
    
    return response

  except Exception as e:
    print(f'Error during code exchange: {e}')

    return None

def exchange_code(code, verifier):
  uri = urljoin(BASE_URI, TOKEN_ENDPOINT)
  data = {
    'client_id': CLIENT_ID,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI,
    'code_verifier': verifier,
    'resource': RESOURCE,
    'scope': REQUEST_SCOPE
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  response = encoded_post(uri, data, headers)
  res = None

  if response:
    try:
      res = response.json()

    except requests.exceptions.JSONDecodeError:
      print(f'Ignoring text response, this might cause an error later...')

    except Exception as e:
      print(f'Error: {e}')
    
  return res


def write_auth_file(tokens):
  if tokens is None:
    input('Failed to exchange authentication code for token. Please try again.')
    exit()
    
  current_dir = os.path.dirname(os.path.abspath(__file__))
  access_token = tokens.get('access_token')
  refresh_token = tokens.get('refresh_token')
  auth_path = os.path.join(current_dir, AUTH_FILENAME)

  if access_token is None:
    input('Failed to exchange authentication code for token. Please try again.')
    exit()

  try:
    with open(auth_path, 'w') as file:
      file.write(f'access-token: {access_token}\n')

      if refresh_token:
        file.write(f'refresh-token: {refresh_token}\n')
    
    input('Created auth.txt successfully. Press Enter to close terminal.')
  
  except Exception as e:
    input(f'Failed to write token to {AUTH_FILENAME}. Please try again.')
    exit()


def check_auth_file():
  current_dir = os.path.dirname(os.path.abspath(__file__))
  auth_path = os.path.join(current_dir, AUTH_FILENAME)

  if os.path.exists(auth_path):
    input('[SUCCESS] Created auth.txt successfully. Press Enter to close terminal.')
  else:
    input('[FAIL] Failed to create auth.txt, please try again.')


def main():
  print_header()

  if len(sys.argv) > 1:
    params = parse_uri(sys.argv[1])
    code = params.get('code', [None])[0]
    verifier = retrieve_verifier()

    tokens = exchange_code(code, verifier)
    write_auth_file(tokens)

  else:
    setup_desktop_entry()
    authenticate()
    check_auth_file()


if __name__ == '__main__':
  main()
