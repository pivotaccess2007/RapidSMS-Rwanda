import os
import sys


filedir = os.path.dirname(__file__)

rootpath = os.path.join(filedir, "..", "..")
sys.path.append(os.path.join(rootpath))
sys.path.append(os.path.join(rootpath,'apps'))
sys.path.append(os.path.join(rootpath,'lib'))
sys.path.append(os.path.join(rootpath,'lib','rapidsms'))
sys.path.append(os.path.join(rootpath,'lib','rapidsms','webui'))


os.environ['RAPIDSMS_INI'] = os.path.join(rootpath,'rapidsms.ini')
os.environ['DJANGO_SETTINGS_MODULE'] = 'rapidsms.webui.settings'
os.environ["RAPIDSMS_HOME"] = rootpath

from rapidsms.webui import settings

sys.path.append('/usr/local/rapidsms')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
