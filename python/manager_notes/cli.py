import argparse
import sys
from pathlib import Path
from .notes import NotesManager


def main(argv=None):
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(prog='manager-notes', description='Daily notes for senior managers')

    sub = parser.add_subparsers(dest='cmd')

    p_init = sub.add_parser('init', help='Initialize notes directory')
    p_init.add_argument('path', nargs='?', help='Path to notes directory', default=None)

    p_new = sub.add_parser('new', help='Create a new dated note')
    p_new.add_argument('title', nargs='?', default='', help='Title for the note')
    p_new.add_argument('--tags', '-t', help='Comma separated tags', default='')
    p_new.add_argument('--no-open', action='store_true', help="Don't open editor")

    p_list = sub.add_parser('list', help='List notes (optionally filter)')
    p_list.add_argument('query', nargs='?', default='', help='Query to filter notes')

    p_show = sub.add_parser('show', help='Print a note to stdout')
    p_show.add_argument('filename', help='Filename to show')

    args = parser.parse_args(argv)

    if args.cmd == 'init':
        nm = NotesManager(args.path)
        print(f'Initialized notes at {nm.base_path}')
        return 0

    nm = NotesManager()

    if args.cmd == 'new':
        tags = [t.strip() for t in args.tags.split(',')] if args.tags else []
        path = nm.create_note(args.title or 'note', tags=tags, open_in_editor=not args.no_open)
        print(f'Created note: {path}')
        return 0

    if args.cmd == 'list':
        results = nm.search(args.query)
        if not results:
            print('No notes found')
            return 0
        for i, r in enumerate(results[:50], start=1):
            print(f"{i:2d}. {r['name']}  (score={r['score']:.2f})")
        return 0

    if args.cmd == 'show':
        print(nm.read_note(args.filename))
        return 0

    parser.print_help()
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
