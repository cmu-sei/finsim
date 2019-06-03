#!/usr/bin/env python
"""
Command-line utility for administrative tasks.
"""
#generic Django code, part of django.core.management package
import os
import sys

if __name__ == "__main__":      #if the current module (the if statement) is being run directly (as in python manage.py) or someone is running it (for example, manage.py is imported into another module)
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",       #set default operating system environment settings
        "xyzbank.settings"
    )

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)     #passes on arguments to get parsed
