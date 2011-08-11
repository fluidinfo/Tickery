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
from twisted.internet import defer

from txfluiddb.client import Object

from tickery import ftwitter
from tickery.cacheutils import DumpingCache
from tickery.www.defaults import TWITTER_USERNAME


class Item(object):
    def __init__(self, uid=None, screenname=None):
        self.uid = uid
        self.screenname = screenname

    def __str__(self):
        return ('name=%-16s uid=%s' %
                (self.screenname if self.screenname else '<unknown>',
                self.uid if self.uid else '<unknown>'))


class OidUidScreennameCache(DumpingCache):

    def __init__(self, endpoint):
        super(OidUidScreennameCache, self).__init__()
        self.endpoint = endpoint

    def load(self, cacheFile):
        self.screennameToObjectId = {}
        self.uidToObjectId = {}
        data = super(OidUidScreennameCache, self).load(cacheFile)
        if data is None:
            self.objectIdToItem = {}
            self.setCache(self.objectIdToItem)
        else:
            self.objectIdToItem = data
            for oid, item in self.objectIdToItem.iteritems():
                if item.uid is not None:
                    self.uidToObjectId[item.uid] = oid
                if item.screenname is not None:
                    self.screennameToObjectId[item.screenname.lower()] = oid

    def __str__(self):
        s = ['%d oids in oid/uid/name cache' % len(self.objectIdToItem)]
        for key in sorted(self.objectIdToItem.keys()):
            s.append('%s: %s' % (key, self.objectIdToItem[key]))
        return '\n'.join(s)

    def nUsers(self):
        return len(self.objectIdToItem)

    def add(self, objectId, uid=None, screenname=None):
        if uid is not None:
            self.uidToObjectId[uid] = objectId
        if screenname is not None:
            self.screennameToObjectId[screenname.lower()] = objectId
        try:
            item = self.objectIdToItem[objectId]
        except KeyError:
            self.objectIdToItem[objectId] = Item(uid, screenname)
            self.clean = False
        else:
            if screenname is not None:
                if item.screenname is None or item.screenname != screenname:
                    item.screenname = screenname
                    self.clean = False
            if uid is not None:
                if item.uid is None or item.uid != uid:
                    item.uid = uid
                    self.clean = False

    def objectIdByScreenname(self, screenname):
        try:
            return defer.succeed(self.screennameToObjectId[screenname.lower()])
        except KeyError:
            def _cb(results):
                nResults = len(results)
                if nResults == 0:
                    raise Exception(
                        'Screenname %r not known to Fluidinfo' % screenname)
                elif nResults == 1:
                    objectId = results[0].uuid
                    self.add(objectId, screenname=screenname)
                    return objectId
                else:
                    log.err('ERROR: Twitter screenname %r found %d times '
                            'in Fluidinfo! ObjectIds = %r' %
                            (screenname, nResults, results))
                    # Don't crash: just return the first object id found.
                    return results[0]
            d = Object.query(self.endpoint, '%s = "%s"' %
                             (ftwitter.screennameTag.getPath(), screenname))
            d.addCallback(_cb)
            return d

    @defer.inlineCallbacks
    def objectByUid(self, uid, screenname=None, userNameCache=None):
        try:
            defer.returnValue(Object(self.uidToObjectId[uid]))
        except KeyError:
            results = yield Object.query(
                self.endpoint, '%s = %s' % (ftwitter.idTag.getPath(), uid))
            nResults = len(results)
            if nResults:
                if nResults > 1:
                    msg = ('User with Twitter id %d exists %d times '
                           'in Fluidinfo! Ignoring.' % (uid, nResults))
                    log.err(msg)
                    raise Exception(msg)
                else:
                    o = results[0]
                    self.add(o.uuid, uid, screenname)
                    log.msg('Found Fluidinfo object for Twitter user %d.' %
                            uid)
            else:
                if screenname is None:
                    assert userNameCache is not None
                    screenname = yield userNameCache.screennameByUid(uid)
                o = yield Object.create(self.endpoint, u'@%s' % screenname)
                log.msg('Made new object for Twitter user %r (uid %d).' %
                        (screenname, uid))
                # TODO: what happens if something goes wrong here?
                yield defer.gatherResults([
                    o.set(self.endpoint, ftwitter.idTag, int(uid)),
                    o.set(self.endpoint, ftwitter.screennameTag, screenname),
                    ])
                log.msg('Set id and screenname tags on obj for '
                        'Twitter user %r' % screenname)
                self.add(o.uuid, uid, screenname)
            defer.returnValue(o)

    def knownUid(self, uid):
        return uid in self.uidToObjectId

    def removeUid(self, uid):
        if uid in self.uidToObjectId:
            objectId = self.uidToObjectId[uid]
            del self.uidToObjectId[uid]
            if objectId in self.objectIdToItem:
                item = self.objectIdToItem[objectId]
                screenname = item.screenname
                if screenname is not None:
                    if screenname in self.screennameToObjectId:
                        del self.screennameToObjectId[screenname]
                del self.objectIdToItem[objectId]
            self.clean = False

    def objectIdsToUsers(self, objectIds, userCache):
        '''Convert a list of Fluidinfo object ids to a 2-tuple, a list of
        Twitter screennames and a list of any Fluidinfo object ids that did
        not correspond to Twitter users.'''
        users = []
        ids = []
        deferreds = []

        for objectId in objectIds:
            try:
                item = self.objectIdToItem[objectId]
            except KeyError:
                ids.append(objectId)
            else:
                if item.screenname is not None:
                    d = userCache.userByScreenname(item.screenname)
                elif item.uid is not None:
                    d = userCache.userByUid(item.uid)
                else:
                    log.err('ObjectId %s has no screenname or uid.' % objectId)
                    d = None

                if d:
                    d.addCallback(lambda u: users.append(u))
                    d.addErrback(log.err)
                    deferreds.append(d)

        d = defer.DeferredList(deferreds)
        d.addCallback(lambda _: (users, ids))
        return d
