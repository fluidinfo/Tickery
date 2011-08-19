"""
Recipes for deploying and starting Tickery on tickery.net.
"""

from __future__ import with_statement
from fabric.api import require, run, local, env, put, cd, settings
from datetime import datetime


def live():
    """
    Define the live host.
    """
    RELEASE = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    env.hosts = ['tickery@tickery.net']
    env.sitename = 'tickery'
    # Perhaps use GIT-VERSION-GEN for a revno, when we understand it?
    # revno = Popen(['bzr', 'revno'], stdout=PIPE).communicate()[0][:-1]
    env.tag = '%s-%s' % (env.sitename, RELEASE)


def upload():
    """
    Upload static files to the server. Note that $HOME for the tickery user
    on tickery.net is /srv/tickery, so all put() have that as their cwd.
    """
    require('hosts', provided_by=[live])

    # Bundle, upload, and extract the bzr sources.
    local('git archive --prefix=%(tag)s/ -v --format tar HEAD | '
          'bzip2 > %(tag)s.tar.bz2' % env)
    put('%(tag)s.tar.bz2' % env, '.')
    run('tar xjvf %(tag)s.tar.bz2' % env)

    # Bundle, upload, and extract our local pyjamas-generated files.
    # Note that this tarball is put into env.tag, which is where it's
    # correctly unpacked.
    local('tar cfvj tickery-pyjs.tar.bz2 '
          'tickery/www/output tickery/admin/output')
    put('tickery-pyjs.tar.bz2', '%(tag)s' % env)
    run('cd %(tag)s && tar xjvf tickery-pyjs.tar.bz2' % env)

    # Create a virtualenv for the new distribution.
    run('virtualenv --no-site-packages %(tag)s' % env)

    # Install requirements.
    run('%(tag)s/bin/pip install --upgrade -r %(tag)s/requirements.txt' % env)

    # Make var/{run,log} dirs for runtime files.
    run('mkdir -p %(tag)s/var/run' % env)
    run('mkdir -p %(tag)s/var/log' % env)

    # Allow other users to see the files/dirs on the remote server.
    run('find %(tag)s -type f -print0 | xargs -0 chmod go+r' % env)
    run('find %(tag)s -type d -print0 | xargs -0 chmod go+rx' % env)


def stop_server():
    """
    Stop any currently running Tickery service.
    """
    require('hosts', provided_by=[live])

    print('Stopping Tickery service....')
    with settings(warn_only=True):
        result = run('cat current/var/run/tickery.pid | xargs -r kill')
        if result.failed:
            print 'No Tickery server was running.'


def _start_server():
    """
    Link the newly uploaded deployment in the right place in the filesystem
    and start the Twisted Tickery service.  Note that you cannot run this
    command by itself, since 'tag' has to be set to an already uploaded
    distribution.
    """
    require('hosts', provided_by=[live])
    run('rm -f current')
    run('ln -s %(tag)s current' % env)
    with cd('current'):
        # For now we're starting Tickery via a shell script. This will be
        # changed to use upstart.
        # run('restart %(sitename)s' % env)
        run('bin/run-tickery.sh')


def deploy():
    """
    Wraps all the steps up to deploy to the live server.
    """
    upload()
    stop_server()
    _start_server()
