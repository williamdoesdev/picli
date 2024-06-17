from os import get_terminal_size

from picli.log import log_buffer, info
from picli.credentials import username, password
from picli.query import active_query, QueryType
from picli.ansi import *
from picli import pi

CREDENTIALS_SECTION_HEIGHT = 2
QUERY_SECTION_HEIGHT = 0
PROMPT_SECTION_HEIGHT = 2
RESULTS_SECTION_HEIGHT = 0
LOG_SECTION_HEIGHT = 0

def render():
    print(ANSI_CLEAR, end='')
    print(ANSI_CURSOR_HOME, end='')
    _render_credentials()
    print()
    _render_query()
    print('\n' * 3, end='')
    if pi.results:
        _render_results()
    _render_log()
    _reset_cursor()

def _render_credentials():
    if username is None and password is None:
        print(f'{ANSI_FG_YELLOW}Not logged in.{ANSI_FG_RESET}')
    else:
        print(f'{ANSI_FG_CYAN}Logged in as: {ANSI_FG_RESET}{username}')

def _render_query():
    global QUERY_SECTION_HEIGHT
    print(f'{ANSI_FG_CYAN}API Base URL: {ANSI_FG_RESET}{active_query.api_base_url}{ANSI_FG_RESET}')
    print(f'{ANSI_FG_CYAN}PI Server: {ANSI_FG_RESET}{active_query.pi_server}{ANSI_FG_RESET}')
    print(f'{ANSI_FG_CYAN}Type: {ANSI_FG_RESET}{active_query.query_type.value}{ANSI_FG_RESET}')
    print(f'{ANSI_FG_CYAN}Start Time: {ANSI_FG_RESET}{active_query.start_time}{ANSI_FG_RESET}')
    print(f'{ANSI_FG_CYAN}End Time: {ANSI_FG_RESET}{active_query.end_time}{ANSI_FG_RESET}')
    print(f'{ANSI_FG_CYAN}Tags: {ANSI_FG_RESET}{", ".join(active_query.tags)}{ANSI_FG_RESET}')
    print(f'{ANSI_FG_CYAN}Timezone: {ANSI_FG_RESET}{active_query.timezone}{ANSI_FG_RESET}')
    if active_query.query_type == QueryType.SUMMARY:
        print(f'{ANSI_FG_CYAN}Summary Type: {ANSI_FG_RESET}{active_query.summary_type.value}{ANSI_FG_RESET}')
        print(f'{ANSI_FG_CYAN}Interval: {ANSI_FG_RESET}{active_query.interval}{ANSI_FG_RESET}')
        print(f'{ANSI_FG_CYAN}Calculation Basis: {ANSI_FG_RESET}{active_query.calculation_basis.value}{ANSI_FG_RESET}')
        print(f'{ANSI_FG_CYAN}Timestamp Calculation: {ANSI_FG_RESET}{active_query.timestamp_calculation.value}{ANSI_FG_RESET}')
        QUERY_SECTION_HEIGHT = 12
    if active_query.query_type == QueryType.INTERPOLATED:
        print(f'{ANSI_FG_CYAN}Interval: {ANSI_FG_RESET}{active_query.interval}{ANSI_FG_RESET}')
        QUERY_SECTION_HEIGHT = 9
    if active_query.query_type == QueryType.RECORDED:
        print(f'{ANSI_FG_CYAN}Boundary Type: {ANSI_FG_RESET}{active_query.boundary_type.value}{ANSI_FG_RESET}')
        QUERY_SECTION_HEIGHT = 9

def _render_results():
    # TODO: Anything but this...
    global RESULTS_SECTION_HEIGHT
    terminal_size = get_terminal_size()
    print(f'{ANSI_FG_CYAN}{"─" * terminal_size.columns}{ANSI_FG_RESET}')
    column_titles = list(pi.results[0].keys())
    # Top border
    print(f' ┌', end='')
    for column in column_titles:
        print(f'{"─" * (len(str.ljust(column, 25)) + 2)}', end='')
        if column != column_titles[-1]:
            print(f'┬', end='')
    print(f'┐')
    # Headers
    print(' │', end='')
    for column in column_titles:
        print(f' {str.ljust(column, 25)} ', end='')
        print(f'│', end='')
    # Bottom header border
    print(f'\n ├', end='')
    for column in column_titles:
        print(f'{"─" * (len(str.ljust(column, 25)) + 2)}', end='')
        if column != column_titles[-1]:
            print(f'┼', end='')
    print(f'┤')
    # Data
    current_row = 0
    for row in pi.results:
        print(' │', end='')
        for column in column_titles:
            data = str(row[column])
            if len(data) > len(str.ljust(column, 25)):
                print(f' {data[:len(str.ljust(column, 25))]} ', end='')
            else:
                print(f' {str.ljust(data, len(str.ljust(column, 25)))} ', end='')
            print(f'│', end='')
        print()
        current_row += 1
        if current_row >= 9:
            break
    # Bottom border
    print(f' └', end='')
    for column in column_titles:
        print(f'{"─" * (len(str.ljust(column, 25)) + 2)}', end='')
        if column != column_titles[-1]:
            print(f'┴', end='')
    print(f'┘')
    print()

    RESULTS_SECTION_HEIGHT = 5 + min(len(pi.results), 10)

def _render_log():
    global LOG_SECTION_HEIGHT
    terminal_size = get_terminal_size()
    log_section_total_height = terminal_size.lines - CREDENTIALS_SECTION_HEIGHT - QUERY_SECTION_HEIGHT - PROMPT_SECTION_HEIGHT - RESULTS_SECTION_HEIGHT
    print(f'{ANSI_FG_CYAN}{"─" * terminal_size.columns}{ANSI_FG_RESET}')
    reversed_buffer = log_buffer[::-1]
    for i, log in enumerate(reversed_buffer):
        if i >= log_section_total_height:
            break
        if len(log) > terminal_size.columns:
            print(log[:terminal_size.columns - 3] + '...')
        else:
            print(log)
    LOG_SECTION_HEIGHT = len(log_buffer)

def _reset_cursor():
    print(ANSI_UP * (4 + LOG_SECTION_HEIGHT + RESULTS_SECTION_HEIGHT), end='')