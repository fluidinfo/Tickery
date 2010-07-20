# Copyright 2010 Fluidinfo Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

from zope.interface import implements

from twisted.plugin import IPlugin
from twisted.application import service, internet
from twisted.web import server
from twisted.web.static import File
from twisted.internet import protocol

from tickery.www import defaults
from tickery.endpoint import twitterEndpoint
from tickery.cache import TickeryCache
from tickery.api import API
from tickery.service import RegularService, AdminService
from tickery.options import EndpointOptions
from tickery import callback


class Options(EndpointOptions):
    optParameters = [
        ['cache-dir', None, 'CACHE', 'The directory for cache files.'],
        ['queue-width', None, 3, 'The initial size of the dispatch queue.'],
        ['port', None, defaults.TICKERY_SERVICE_PORT, 'The port to listen on.'],
        ]
    optFlags = [
        ['noisy-logging', None, "If True, let factories log verbosely."],
        ['promiscuous', None, "If True, allow connections on all interfaces."],
        ['restore-add-queue', None,
         "If True, start adding users where we left off last time."],
        ]


class ServiceMaker(object):
    implements(service.IServiceMaker, IPlugin)
    tapname = 'tickery'
    description = "Fluidinfo's Twitter query service."
    options = Options

    def makeService(self, options):
        if not options['noisy-logging']:
            protocol.Factory.noisy = False
            
        endpoint = twitterEndpoint(options['endpoint'])
        tickeryService = service.MultiService()
        cache = TickeryCache(
            options['cache-dir'], options['restore-add-queue'],
            int(options['queue-width']), endpoint)
        cache.setServiceParent(tickeryService)
        
        root = File('www/output')
        root.putChild('tickery', RegularService(cache, endpoint))
        root.putChild(defaults.TICKERY_CALLBACK_CHILD, callback.Callback(cache))
        
        adminRoot = File('admin/output')
        adminRoot.putChild('tickery', AdminService(cache))
        root.putChild('admin', adminRoot)

        root.putChild('api', API(cache))
        
        factory = server.Site(root)
        if options['promiscuous']:
            kw = {}
        else:
            kw = { 'interface' : 'localhost' }
        tickeryServer = internet.TCPServer(int(options['port']), factory, **kw)
        tickeryServer.setServiceParent(tickeryService)
        
        return tickeryService

serviceMaker = ServiceMaker()

### Local Variables:
### eval: (rename-buffer "tickery plugin")
### End:
