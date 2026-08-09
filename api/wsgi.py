import os
import sys

# Ensure repo's inner project directory is on sys.path so the settings module
# `church_project.settings` can be imported when Vercel executes this file.
ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, "church_project"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "church_project.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
