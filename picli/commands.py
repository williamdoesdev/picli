from typing import Callable, Optional
from enum import Enum
from inspect import signature
from dataclasses import dataclass

from picli import config
from picli.errors import PICLICommandError

@dataclass
class Command:
    primary_command: str 
    subcommands: list[str]
    callback: Callable

class ParsingPhase(Enum):
    PRIMARY_COMMAND = 1
    SUBCOMMAND = 2
    ARGUMENT = 3

_all_commands: list[Command] = []
_command_execution_queue: list[tuple[Command, list[str]]] = []

_parse_phase: ParsingPhase = ParsingPhase.PRIMARY_COMMAND
_command_search_pool: list[Command] = []
_working_primary_command: Optional[str] = None
_working_subcommands: list[str] = []
_working_arguments: list[str] = []

def register_command(callback: Callable, command_chain: list[str]) -> None:
        primary_command = command_chain[0]
        subcommands = command_chain[1:]
        _all_commands.append(Command(primary_command=primary_command, subcommands=subcommands, callback=callback))

def _parse_primary_command(item: str) -> None:
    global _parse_phase, _command_search_pool, _working_primary_command
    _command_search_pool = list(filter(lambda command: command.primary_command == item, _command_search_pool))
    if len(_command_search_pool) == 0:
        raise PICLICommandError('Command not found.')
    _working_primary_command = item
    _parse_phase = ParsingPhase.SUBCOMMAND

def _parse_subcommand(item: str) -> None:
    global _parse_phase, _command_search_pool, _working_primary_command, _working_subcommands
    subcommands = _working_subcommands + [item]
    search_pool = list(filter(lambda command: command.subcommands[:len(subcommands)] == subcommands, _command_search_pool))
    if len(search_pool) == 0:
        _parse_phase = ParsingPhase.ARGUMENT
        return
    _working_subcommands = subcommands
    _command_search_pool = search_pool

def _check() -> None:
    global _command_search_pool, _working_subcommands, _working_arguments
    for command in _command_search_pool:
        if command.primary_command == _working_primary_command and command.subcommands == _working_subcommands and len(signature(command.callback).parameters) == len(_working_arguments):
            _command_execution_queue.append((command, _working_arguments))
            _reset()

def _parse_argument(item: str) -> None:
    _working_arguments.append(item)

def parse(command_chain: list[str]) -> None:
    _reset()
    for item in command_chain:
        if _parse_phase == ParsingPhase.PRIMARY_COMMAND:
            _parse_primary_command(item)
        elif _parse_phase == ParsingPhase.SUBCOMMAND:
            _parse_subcommand(item)
        if _parse_phase == ParsingPhase.ARGUMENT:
            _parse_argument(item)
        _check()
    if _working_primary_command is not None or _working_subcommands != [] or _working_arguments != []:
        raise PICLICommandError('Command not found')
    _execute()

def _reset() -> None:
    global _parse_phase, _command_search_pool, _working_primary_command, _working_subcommands, _working_arguments
    _parse_phase = ParsingPhase.PRIMARY_COMMAND
    _command_search_pool = _all_commands
    _working_primary_command = None
    _working_subcommands = []
    _working_arguments = []

def _execute() -> None:
    for command, arguments in _command_execution_queue:
        command.callback(*arguments)
    _command_execution_queue.clear()

def _list_commands() -> None:
    for command in _all_commands:
        print(f'{command.primary_command} {command.subcommands}')