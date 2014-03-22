#!/usr/bin/env python
# pymode:lint_ignore=E501
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coffeestats.settings.local")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
