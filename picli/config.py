from enum import Enum
from typing import Optional, Any, get_type_hints
import platform
from os import path
import os
import json
from inspect import isclass

from picli.errors import PICLIConfigError, PICLIInitError
from picli.commands import register_command

class AuthMethod(Enum):
    BASIC = 'basic'
    NTLM = 'ntlm'

auth_method: AuthMethod = AuthMethod.BASIC
store_credentials: bool = False
request_fields_to_save: list[str] = ['api_base_url', 'pi_server']
output_file_path: Optional[str] = None
tls_cert_path: Optional[str] = None
debug_mode: bool = False

def _populate_from_file() -> None:
    global auth_method, store_credentials, request_fields_to_save, output_file_path, tls_cert_path, debug_mode
    if platform.system() == 'Windows':
        config_path = path.join(path.expanduser('~'), 'AppData', 'Local', 'picli', 'config.json')
    elif platform.system() == 'Linux':
        config_path = path.join(path.expanduser('~'), '.config', 'picli', 'config.json')
    else:
        raise PICLIInitError('Unsupported operating system. Don\'t know where to look for config file.')
    
    if not path.isfile(config_path):
        try:
            os.makedirs(path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as file:
                file.write(json.dumps({
                    'auth_method': auth_method,
                    'store_credentials': store_credentials,
                    'request_fields_to_save': request_fields_to_save,
                    'output_file_path': output_file_path,
                    'tls_cert_path': tls_cert_path,
                    'debug_mode': debug_mode
                }, default=str, indent=4))
        except FileNotFoundError:
            raise PICLIInitError(f'Could not create config file at {config_path}.')

    with open(config_path, 'r') as file:
        config_file_contents = json.loads(file.read())
        auth_method = AuthMethod(config_file_contents['auth_method'])
        store_credentials = config_file_contents['store_credentials']
        request_fields_to_save = config_file_contents['request_fields_to_save']
        output_file_path = config_file_contents['output_file_path']
        tls_cert_path = config_file_contents['tls_cert_path']
        debug_mode = config_file_contents['debug_mode']
            
def _populate_from_env() -> None:
    global auth_method, store_credentials, request_fields_to_save, output_file_path, tls_cert_path, debug_mode
    if 'PICLI_AUTH_METHOD' in os.environ:
        auth_method = AuthMethod(os.environ['PICLI_AUTH_METHOD'])
    if 'PICLI_STORE_CREDENTIALS' in os.environ:
        store_credentials = bool(os.environ['PICLI_STORE_CREDENTIALS'])
    if 'PICLI_REQUEST_FIELDS_TO_SAVE' in os.environ:
        request_fields_to_save = os.environ['PICLI_REQUEST_FIELDS_TO_SAVE'].split(',')
    if 'PICLI_OUTPUT_FILE_PATH' in os.environ:
        output_file_path = os.environ['PICLI_OUTPUT_FILE_PATH']
    if 'PICLI_TLS_CERT_PATH' in os.environ:
        tls_cert_path = os.environ['PICLI_TLS_CERT_PATH']
    if 'PICLI_DEBUG_MODE' in os.environ:
        debug_mode = bool(os.environ['PICLI_DEBUG_MODE'])

def set_auth_method(method: str) -> None:
    '''Sets the authentication method for the PI Web API.'''
    global auth_method
    try:
        auth_method = AuthMethod.from_string_insensitive(method)
    except ValueError:
        raise PICLIConfigError(f'Invalid authentication method {method}. Must be one of {", ".join([auth.value for auth in AuthMethod])}.')
register_command(set_auth_method, ['config', 'set', 'auth_method'])

def set_store_credentials(value: str) -> None:
    '''Sets whether to store credentials for future use.'''
    global store_credentials
    if value.lower() not in ['true', 'false']:
        raise PICLIConfigError(f'Invalid value {value}. Must be either "true" or "false".')
    store_credentials = bool(value)
register_command(set_store_credentials, ['config', 'set', 'store_credentials'])

def set_request_fields_to_save(fields: str) -> None:
    '''Sets the fields to save between sessions.'''
    global request_fields_to_save
    if ';' in fields:
        fields = fields.split(';')
    elif ',' in fields:
        fields = fields.split(',')
    elif '|' in fields:
        fields = fields.split('|')
    else:
        fields = [fields]
    request_fields_to_save = fields
register_command(set_request_fields_to_save, ['config', 'set', 'request_fields_to_save'])

def set_output_file_path(path: str) -> None:
    '''Sets the path to save output to.'''
    global output_file_path
    output_file_path = path
register_command(set_output_file_path, ['config', 'set', 'output_file_path'])

def set_tls_cert_path(path: str) -> None:
    '''Sets the path to the TLS certificate to use.'''
    global tls_cert_path
    tls_cert_path = path
register_command(set_tls_cert_path, ['config', 'set', 'tls_cert_path'])

def set_debug_mode(value: str) -> None:
    '''Sets whether to output debug information.'''
    global debug_mode
    if value.lower() not in ['true', 'false']:
        raise PICLIConfigError(f'Invalid value {value}. Must be either "true" or "false".')
    debug_mode = bool(value)
register_command(set_debug_mode, ['config', 'set', 'debug_mode'])

_populate_from_file()
_populate_from_env()