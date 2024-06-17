from enum import Enum
import platform
from os import path
from typing import List
import os
from dataclasses import dataclass, field
from dateutil.parser import parse
import json

from picli.errors import PICLIInitError, PICLIShutdownError
from picli import config
from picli.commands import register_command
from picli.log import info

# Monkeypatching this method onto enum so that I can easily convert a string taken from user input
def from_string_insensitive(cls, value: str): 
    value = value.lower()
    for member in cls:
        if member.value.lower() == value:
            return member
    raise ValueError(f"'{value}' is not a valid {cls.__name__}")
Enum.from_string_insensitive = classmethod(from_string_insensitive)

class QueryType(Enum):
    RECORDED = 'Recorded'
    INTERPOLATED = 'Interpolated'
    SUMMARY = 'Summary'

class SummaryType(Enum):
    TOTAL = "Total"
    AVERAGE = "Average"
    MINIMUM = "Minimum"
    MAXIMUM = "Maximum"
    STANDARD_DEVIATION = "StdDev"
    POPULATION_STANDARD_DEVIATION = "PopulationStdDev"
    COUNT = "Count"

class CalculationBasis(Enum):
    TIME_WEIGHTED = "TimeWeighted"
    EVENT_WEIGHTED = "EventWeighted"
    TIME_WEIGHTED_CONTINUOUS = "TimeWeightedContinuous"
    TIME_WEIGHTED_DISCRETE = "TimeWeightedDiscrete"
    EVENT_WEIGHTED_EXCLUDE_MOST_RECENT_EVENT = "EventWeightedExcludeMostRecentEvent"
    EVENT_WEIGHTED_EXCLUDE_EARLIEST_EVENT = "EventWeightedExcludeEarliestEvent"
    EVENT_WEIGHTED_INCLUDE_BOTH_ENDS = "EventWeightedIncludeBothEnds"

class TimestampCalculation(Enum):
    AUTO = "Auto"
    EARLIEST = "EarliestTime"
    MOST_RECENT = "MostRecentTime"

class BoundaryType(Enum):
    INSIDE = "Inside"
    OUTSIDE = "Outside"
    INTERPOLATED = "Interpolated"

@dataclass
class Query:
    query_number: int = 1
    query_type: QueryType = QueryType.RECORDED
    api_base_url: str = 'https://piwebapi.domain.com'
    pi_server: str = 'piserver'
    start_time: str = '*-1d'
    end_time: str = '*'
    tags: List[str] = field(default_factory=list)
    timezone: str = 'UTC'
    summary_type: SummaryType = SummaryType.AVERAGE
    calculation_basis: CalculationBasis = CalculationBasis.TIME_WEIGHTED
    timestamp_calculation: TimestampCalculation = TimestampCalculation.AUTO
    boundary_type: BoundaryType = BoundaryType.INSIDE
    interval: str = '1d'

    def __post_init__(self):
        self._populate_from_file() 

    def __del__(self):
        self._save()

    def _populate_from_file(self) -> None:
        global query_1, query_2
        if platform.system() == 'Windows':
            save_path = path.join(path.expanduser('~'), 'AppData', 'Local', 'picli', 'save.json')
        elif platform.system() == 'Linux':
            save_path = path.join(path.expanduser('~'), '.local', 'share', 'picli', 'save.json')
        else:
            raise PICLIInitError('Unsupported operating system. Don\'t know where to look for save file.')
        if not path.isfile(save_path):
            try:
                os.makedirs(path.dirname(save_path), exist_ok=True)
                with open(save_path, 'w') as file:
                    file.write(r'{"1": {}, "2": {}}')
            except FileNotFoundError:
                raise PICLIInitError(f'Could not create save file at {save_path}.')
            
        with open(save_path, 'r') as file:
            save_file_contents = json.loads(file.read())
            for field, value in save_file_contents[str(self.query_number)].items():
                if field in config.request_fields_to_save:
                    setattr(self, field, value)

    def _save(self) -> None:
        if platform.system() == 'Windows':
            save_path = path.join(path.expanduser('~'), 'AppData', 'Local', 'picli', 'save.json')
        elif platform.system() == 'Linux':
            save_path = path.join(path.expanduser('~'), '.local', 'share', 'picli', 'save.json')
        else:
            raise PICLIShutdownError('Unsupported operating system. Don\'t know where to look for save file.')
        
        save_file_contents = {"1": {}, "2": {}}
        for field in self.__dataclass_fields__:
            if field in config.request_fields_to_save:
                save_file_contents[str(self.query_number)][field] = getattr(self, field)
        with open(save_path, 'w') as file:
            file.write(json.dumps(save_file_contents, default=str, indent=4))

query_1 = Query(query_number=1)
query_2 = Query(query_number=2)
active_query = query_1

def swap_queries():
    '''Swaps the currently active query.'''
    info('Swapping queries.')
    global active_query
    if active_query == query_1:
        active_query = query_2
    else:
        active_query = query_1
register_command(swap_queries, ['swap'])

def set_query_type(query_type: str):
    '''Sets the query type for the active query.'''
    info(f'Setting query type to {query_type}.')
    active_query.query_type = QueryType.from_string_insensitive(query_type)
register_command(set_query_type, ['type'])

def set_api_base_url(url: str):
    '''Sets the API base URL for the active query.'''
    info(f'Setting API base URL to {url}.')
    active_query.api_base_url = url
register_command(set_api_base_url, ['url'])

def set_pi_server(server: str):
    '''Sets the PI server for the active query.'''
    info(f'Setting PI server to {server}.')
    active_query.pi_server = server
register_command(set_pi_server, ['server'])

def set_start_time(time: str):
    '''Sets the start time for the active query.'''
    info(f'Setting start time to {time}.')
    try:
        datetime = parse(time)
        active_query.start_time = datetime.isoformat()
    except ValueError:
        active_query.start_time = time
register_command(set_start_time, ['start'])

def set_end_time(time: str):
    '''Sets the end time for the active query.'''
    info(f'Setting end time to {time}.')
    try:
        datetime = parse(time)
        active_query.end_time = datetime.isoformat()
    except ValueError:
        active_query.end_time = time
register_command(set_end_time, ['end'])

def add_tags(tags: str):
    '''Adds tags to the active query. Can be comma, semicolon, or pipe separated.'''
    info(f'Adding tags: {tags}.')
    if ',' in tags:
        active_query.tags.extend(tags.split(','))
    elif ';' in tags:
        active_query.tags.extend(tags.split(';'))
    elif '|' in tags:
        active_query.tags.extend(tags.split('|'))
    else:
        active_query.tags.append(tags)
register_command(add_tags, ['tags', 'add'])

def remove_tags(tags: str):
    '''Removes tags from the active query. Can be comma, semicolon, or pipe separated.'''
    info(f'Removing tags: {tags}.')
    if ',' in tags:
        for tag in tags.split(','):
            active_query.tags.remove(tag)
    elif ';' in tags:
        for tag in tags.split(';'):
            active_query.tags.remove(tag)
    elif '|' in tags:
        for tag in tags.split('|'):
            active_query.tags.remove(tag)
    else:
        active_query.tags.remove(tags)
register_command(remove_tags, ['tags', 'remove'])

def set_tags(tags: str):
    '''Sets the tags for the active query. Can be comma, semicolon, or pipe separated.'''
    info(f'Setting tags: {tags}.')
    active_query.tags = []
    if ',' in tags:
        active_query.tags = tags.split(',')
    elif ';' in tags:
        active_query.tags = tags.split(';')
    elif '|' in tags:
        active_query.tags = tags.split('|')
    else:
        active_query.tags = [tags]
register_command(set_tags, ['tags', 'set'])

def clear_tags():
    '''Clears the tags for the active query.'''
    info('Clearing tags.')
    active_query.tags = []
register_command(clear_tags, ['tags', 'clear'])

def set_timezone(timezone: str):
    '''Sets the timezone for the active query.'''
    info(f'Setting timezone to {timezone}.')
    active_query.timezone = timezone
register_command(set_timezone, ['timezone'])

def set_summary_type(summary_type: str):
    '''Sets the summary type for the active query.'''
    info(f'Setting summary type to {summary_type}.')
    active_query.summary_type = SummaryType.from_string_insensitive(summary_type)
register_command(set_summary_type, ['summary'])

def set_calculation_basis(calculation_basis: str):
    '''Sets the calculation basis for the active query.'''
    info(f'Setting calculation basis to {calculation_basis}.')
    active_query.calculation_basis = CalculationBasis.from_string_insensitive(calculation_basis)
register_command(set_calculation_basis, ['basis'])

def set_timestamp_calculation(timestamp_calculation: str):
    '''Sets the timestamp calculation for the active query.'''
    info(f'Setting timestamp calculation to {timestamp_calculation}.')
    active_query.timestamp_calculation = TimestampCalculation.from_string_insensitive(timestamp_calculation)
register_command(set_timestamp_calculation, ['timecalc'])

def set_boundary_type(boundary_type: str):
    '''Sets the boundary type for the active query.'''
    info(f'Setting boundary type to {boundary_type}.')
    active_query.boundary_type = BoundaryType.from_string_insensitive(boundary_type)
register_command(set_boundary_type, ['bound'])

def set_interval(interval: str):
    '''Sets the interval for the active query.'''
    info(f'Setting interval to {interval}.')
    active_query.interval = interval
register_command(set_interval, ['interval'])