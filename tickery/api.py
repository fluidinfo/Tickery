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

from twisted.python import log
from twisted.web import server, resource, error, http

def _returnUID(obj, request):
    uid = str(obj.uuid)
    request.setHeader('Content-length', str(len(uid)))
    request.setHeader('Content-type', 'text/plain')
    request.write(uid)
    request.finish()

def _error(failure, request):
    if failure.check(error.Error):
        code = int(failure.value.status)
    else:
        code = http.BAD_REQUEST
    ep = error.ErrorPage(code, 'An error was encountered', str(failure.value))
    response = ep.render(request)
    request.setHeader('Content-length', str(len(response)))
    request.write(response)
    request.finish()


class API(resource.Resource):
    
    def __init__(self, cache):
        resource.Resource.__init__(self)
        self.cache = cache
        self.putChild('uids', UIDs(self.cache))
        self.putChild('screennames', Screennames(self.cache))

    def getChild(self, what, request):
        return error.ErrorPage(
            http.NOT_FOUND, 'Huh?', "I don't know anything about %r." % what)


class UIDs(resource.Resource):

    allowedMethods = ('GET',)
    
    def __init__(self, cache):
        resource.Resource.__init__(self)
        self.cache = cache

    def getChild(self, uid, request):
        if uid == '':
            return self
        else:
            try:
                uid = int(uid)
            except ValueError:
                return error.ErrorPage(
                    http.BAD_REQUEST,
                    'Malformed UID',
                    'The value you supplied (%r) could not be converted '
                    'to an integer.' % uid)
            else:
                log.msg('API: request for uid %d.' % uid)
                return UID(uid, self.cache)


class UID(resource.Resource):

    allowedMethods = ('GET',)
    isLeaf = True
    
    def __init__(self, uid, cache):
        resource.Resource.__init__(self)
        self.uid = uid
        self.cache = cache

    def render_GET(self, request):
        d = self.cache.oidUidScreennameCache.objectByUid(
            self.uid, userNameCache=self.cache.userCache)
        d.addCallback(_returnUID, request)
        d.addErrback(_error, request)
        return server.NOT_DONE_YET
    

class Screennames(resource.Resource):

    allowedMethods = ('GET',)    
    
    def __init__(self, cache):
        resource.Resource.__init__(self)
        self.cache = cache
    
    def getChild(self, screenname, request):
        if screenname == '':
            return self
        else:
            log.msg('API: request for screenname %r.' % screenname)
            return Screenname(screenname, self.cache)


class Screenname(resource.Resource):

    allowedMethods = ('GET',)    
    isLeaf = True
    
    def __init__(self, screenname, cache):
        resource.Resource.__init__(self)
        self.screenname = screenname
        self.cache = cache

    def _getObjectId(self, uid, request):
        d = self.cache.oidUidScreennameCache.objectByUid(
            uid, screenname=self.screenname)
        d.addCallback(_returnUID, request)
        return d
    
    def render_GET(self, request):
        d = self.cache.userCache.uidByScreenname(self.screenname)
        d.addCallback(self._getObjectId, request)
        d.addErrback(_error, request)
        return server.NOT_DONE_YET
