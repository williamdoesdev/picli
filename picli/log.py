from logging import Handler, getLogger

from picli import config
from picli.commands import register_command, _all_commands

log_buffer = []

class BufferHandler(Handler):
    def emit(self, record):
        log_buffer.append(self.format(record))

logger = getLogger('picli')
logger.addHandler(BufferHandler())
if config.debug_mode:
    logger.setLevel('DEBUG')
else:
    logger.setLevel('INFO')

info = logger.info
debug = logger.debug

def flush() -> None:
    '''Clears logs.'''
    log_buffer.clear()
register_command(flush, ['logs', 'clear'])

def log_config() -> None: # Putting this here to avoid a circular import ven though it's not that intuitive
    '''Logs the current configuration.'''
    info('Current configuration:')
    info(f'auth_method: {config.auth_method.value}')
    info(f'store_credentials: {config.store_credentials}')
    info(f'request_fields_to_save: {config.request_fields_to_save}')
    info(f'output_file_path: {config.output_file_path}')
    info(f'tls_cert_path: {config.tls_cert_path}')
    info(f'debug_mode: {config.debug_mode}')
register_command(log_config, ['config', 'show'])

def list_commands() -> None: # Same as above
    '''Lists all available commands.'''
    for command in _all_commands:
        info(f'{command.primary_command} {" ".join(command.subcommands)} - {command.callback.__doc__}')
register_command(list_commands, ['help'])