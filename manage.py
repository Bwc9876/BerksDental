#!/usr/bin/env python
"""
    This is a file auto-generated by django that allows for various management commands.
    We use it through cmd to update the database and collect static files.
    When we're debugging, we run the server through this as well.
"""

import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BerksDentalAssistants.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
