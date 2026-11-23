#!/usr/bin/env python
"""
Thin wrapper around the Django management command.

  python scripts/seed_products.py
  python scripts/seed_products.py --clear
  python scripts/seed_products.py --dry-run

Equivalent: python manage.py seed_products [options]
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shopify.settings")

import django  # noqa: E402

django.setup()

from django.core.management import call_command  # noqa: E402

if __name__ == "__main__":
    call_command("seed_products", *sys.argv[1:])