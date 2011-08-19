"""
This fabfile contains recipes for deploying and starting Tickery
(tickery.net).
"""
from __future__ import with_statement
from fabric.api import require, run, local, env, put
from datetime import datetime
from subprocess import Popen, PIPE

def live():
    """
    Define the live host.
    """
    RELEASE = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
    env.hosts = ['tickery@tickery.net']
    env.sitename = 'tickery'
    revno = Popen(['bzr', 'revno'], stdout=PIPE).communicate()[0][:-1]
    env.tag = '%s-r%s-%s' % (env.sitename, revno, RELEASE)


def upload():
    """
    Upload static files to the server. Note that $HOME for the tickery user
    on tickery.net is /srv/tickery, so all put() have that as their cwd.
    """
    require('hosts', provided_by=[live])

    # Bundle, upload, and extract the bzr sources.
    local('bzr export --root=%(tag)s %(tag)s.tar.bz2' % env)
    put('%(tag)s.tar.bz2' % env, '.')
    run('tar xjvf %(tag)s.tar.bz2' % env)

    # Bundle, upload, and extract our local pyjamas-generated .js and .html
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


def configure_server():
    """
    Link the newly uploaded deployment in the right place in the filesystem
    and start the Twisted Tickery server.
    """
    require('hosts', provided_by=[live])
    run('rm -f current' % env)
    run('ln -s %(tag)s current' % env)

    # For when we upgrade to 10.04 and have a modern version of upstart:
    # I'm not sure that restart is right here. If it's not already running
    # restart doesn't do anything. Better to do stop || true, then start?
    # run('restart %(sitename)s' % env)

    # For now we're starting Tickery on a Hardy machine via a shell script.
    run('%(tag)s)/bin/run-tickery.sh' % env)


def deploy():
    """
    Wraps all the steps up to deploy to the live server.
    """
    upload()
    configure_server()
