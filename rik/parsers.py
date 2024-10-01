import argparse
from .integrity.hash import SUPPORTED_HASHES

def add_base_parser_options(parser):

    parser.add_argument(
        'target',
        default = None,
        help    = "Target File or Directory to process",
        metavar = 'TARGET',
        type    = str,
    )

    parser.add_argument(
        '-v', '--verbose',
        action  = 'count',
        default = 0,
        dest    = 'verbose',
        help    = "Increase verbosity",
    )

    parser.add_argument(
        '-q', '--quiet',
        action  = 'count',
        default = 0,
        dest    = 'quiet',
        help    = "Decrease verbosity",
    )

    parser.add_argument(
        '-i', '--integrity',
        choices  = [ 'par2', ] + SUPPORTED_HASHES,
        default  = None,
        dest     = 'integrity',
        help     = 'Integrity to use',
        required = True,
    )

    parser.add_argument(
        '-s', '--size',
        action  = 'append',
        default = [],
        dest    = 'size_constraints',
        help    = 'Add size constraint',
    )

    parser.add_argument(
        '-e', '--exclude',
        action  = 'append',
        default = [],
        dest    = 'excludes',
        help    = 'Exclude files/directories',
    )

    parser.add_argument(
        default = None,
        dest    = 'iargs',
        metavar = 'INTEGRITY_ARGS',
        nargs   = argparse.REMAINDER,
        help    = 'Arguments for integrity',
    )

def add_create_parser(subparsers, parents):
    parser = subparsers.add_parser(
        'create', help = 'Create Integrity', parents = parents
    )
    parser.add_argument(
        '--overwrite',
        action  = 'store_true',
        default = False,
        dest    = 'recalc',
        help    = "Recalculate and overwrite existing integirities",
    )

def add_verify_parser(subparsers, parents):
    _parser = subparsers.add_parser(
        'verify', help = 'Verify Integrity', parents = parents
    )

def add_prune_parser(subparsers, parents):
    _parser = subparsers.add_parser(
        'prune', help = 'Delete Obsolete Integrities', parents = parents
    )

def create_rik_parser():
    parser = argparse.ArgumentParser(
        description = "Recursive Integrity keeper"
    )

    base_parser = argparse.ArgumentParser(add_help = False)
    add_base_parser_options(base_parser)

    subparsers = parser.add_subparsers(dest = 'cmd', help = 'Command')
    subparsers.required = True

    add_create_parser(subparsers, [ base_parser, ])
    add_verify_parser(subparsers, [ base_parser, ])
    add_prune_parser (subparsers, [ base_parser, ])

    return parser

