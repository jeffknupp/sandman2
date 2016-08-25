#!/usr/bin/env python
"""sandman2ctl is a wrapper around the sandman2 library, which creates REST API
services automatically from existing databases."""

import argparse
from sandman2 import get_app


def main():
    """Main entry point for script."""
    parser = argparse.ArgumentParser(
        description='Auto-generate a RESTful API service '
        'from an existing database.'
        )
    parser.add_argument(
        'URI',
        help='Database URI in the format '
             'postgresql+psycopg2://user:password@host/database')
    parser.add_argument(
        '-d',
        '--debug',
        help='Turn on debug logging',
        action='store_true',
        default=False)
    parser.add_argument(
        '-p',
        '--port',
        help='Port for service to listen on',
        default=5000)
    parser.add_argument(
        '-l',
        '--local-only',
        help='Only provide service on localhost (will not be accessible'
             ' from other machines)',
        action='store_true',
        default=False)
    parser.add_argument(
        '-r',
        '--read-only',
        help='Make all database resources read-only (i.e. only the HTTP GET method is supported)',
        action='store_true',
        default=False)
    parser.add_argument(
        '-s',
        '--schema',
        help='Use this named schema instead of default',
        default=None)


    args = parser.parse_args()
    app = get_app(args.URI, read_only=args.read_only, schema=args.schema)
    if args.debug:
        app.config['DEBUG'] = True
    if args.local_only:
        host = '127.0.0.1'
    else:
        host = '0.0.0.0'
    app.config['SECRET_KEY'] = '42'
    app.run(host=host, port=int(args.port))


if __name__ == '__main__':
    main()
