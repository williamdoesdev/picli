from time import sleep

from picli.log import info
from picli.commands import parse
from picli.render import render
from picli.ansi import ANSI_CLEAR, ANSI_CURSOR_HOME
from picli import pi
from picli.query import active_query

def main() -> None:
    try:
        while True:
            render()
            command = input('Enter a command: ')
            try:
                parse(command.split(' '))
            except Exception as e:
                info(e)
    except KeyboardInterrupt:
        active_query._save()
        print(ANSI_CLEAR, end='')
        print(ANSI_CURSOR_HOME, end='')
        exit(0)

if __name__ == '__main__':
    main()