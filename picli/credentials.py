from typing import Optional
from getpass import getpass

from keyring import get_password, set_password, delete_password

from picli import config
from picli.commands import register_command

username: Optional[str] = ''
password: Optional[str] = ''

if config.store_credentials:
    username = get_password('picli', 'username')
    password = get_password('picli', 'password')

def login():
    '''Sets credentials to use for authentication.'''
    global username, password
    username = input('Username: ')
    password = getpass('Password: ')

    if config.store_credentials:
        set_password('picli', 'username', username)
        set_password('picli', 'password', password)
register_command(login, ['login'])

def logout():
    '''Clears stored credentials.'''
    global username, password
    username = None
    password = None

    if config.store_credentials:
        delete_password('picli', 'username')
        delete_password('picli', 'password')
register_command(logout, ['logout'])