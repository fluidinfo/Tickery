#!/usr/bin/env python

import glob
from distutils.core import setup

from tickery.version import version

# Where Tickery files such as the HTML, Javascript, and the Twisted plugin
# should be installed on the destination host:
TICKERY_ROOT = '/opt/tickery'

setup(name='tickery',
      version=version,
      scripts=glob.glob('bin/*.py'),
      packages=['tickery', 'tickery.test'],
      data_files=[
          ('%s/twisted/plugins' % TICKERY_ROOT,
           ['twisted/plugins/tickery_service.py']),

          ('%s/tickery' % TICKERY_ROOT,
           ['tickery/Makefile']),

          # Public (www) files:
          ('%s/tickery/www' % TICKERY_ROOT,
           ['tickery/www/Makefile'] + glob.glob('tickery/www/*.py')),

          ('%s/tickery/www/public' % TICKERY_ROOT,
           glob.glob('tickery/www/public/*')),

          # Admin files:
          ('%s/tickery/admin' % TICKERY_ROOT,
           ['tickery/admin/Makefile'] + glob.glob('tickery/admin/*.py')),

          ('%s/tickery/admin/public' % TICKERY_ROOT,
           glob.glob('tickery/admin/public/*'))
          ],

      maintainer='Fluidinfo Inc.',
      maintainer_email='info@fluidinfo.com',
      url='http://fluidinfo.com/')
