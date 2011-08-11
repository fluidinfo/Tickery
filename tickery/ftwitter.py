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

import time
import urllib

from twisted.internet import defer, task
from twisted.python import log, failure
from twisted.web import http, error

from txfluiddb.client import Object, Tag, Namespace

from tickery import twitter, query, error as terror
from tickery.www import defaults
from tickery.www.defaults import (TICKERY_URL, TWITTER_USERNAME,
    TWITTER_USERS_NAMESPACE_NAME, TWITTER_ID_TAG_NAME,
    TWITTER_SCREENNAME_TAG_NAME, TWITTER_UPDATED_AT_TAG_NAME,
    TWITTER_FRIENDS_NAMESPACE_NAME, TWITTER_N_FRIENDS_TAG_NAME,
    TWITTER_N_FOLLOWERS_TAG_NAME, TWITTER_N_STATUSES_TAG_NAME)

# This is the maximum requests that will be sent out at once by anything
# using a task.Cooperator. That's usually Fluidinfo, but it can also mean
# this many requests going at once to Twitter to pick up user details.
MAX_SIMULTANEOUS_REQUESTS = 5

BITLY_URL_LEN = 20

WORK_TO_CREATE_A_FRIEND = 3
WORK_TO_TAG_A_FRIEND = 1

# Put this into www/defaults and re-org stuff in www/*.py in another branch.
tabName = {
    'simple': 'simple',
    'intermediate': 'intermediate',
    'advanced': 'advanced',
    }

_hashTag = '#tickery'

idTag = Tag(TWITTER_USERNAME,
            TWITTER_USERS_NAMESPACE_NAME,
            TWITTER_ID_TAG_NAME)

screennameTag = Tag(TWITTER_USERNAME,
                    TWITTER_USERS_NAMESPACE_NAME,
                    TWITTER_SCREENNAME_TAG_NAME)

updatedTag = Tag(TWITTER_USERNAME,
                 TWITTER_USERS_NAMESPACE_NAME,
                 TWITTER_UPDATED_AT_TAG_NAME)

nFriendsTag = Tag(TWITTER_USERNAME,
                  TWITTER_USERS_NAMESPACE_NAME,
                  TWITTER_N_FRIENDS_TAG_NAME)

nFollowersTag = Tag(TWITTER_USERNAME,
                    TWITTER_USERS_NAMESPACE_NAME,
                    TWITTER_N_FOLLOWERS_TAG_NAME)

nStatusesTag = Tag(TWITTER_USERNAME,
                   TWITTER_USERS_NAMESPACE_NAME,
                   TWITTER_N_STATUSES_TAG_NAME)

# The Twitter tags we additionally add to user objects. There are several
# others we could add to this.
extraTags = {
    TWITTER_N_FRIENDS_TAG_NAME: nFriendsTag,
    TWITTER_N_FOLLOWERS_TAG_NAME: nFollowersTag,
    TWITTER_N_STATUSES_TAG_NAME: nStatusesTag,
    }


class UnknownScreenname(Exception):
    pass


class UnaddedScreennames(Exception):
    pass


class ScreennameErrors(Exception):
    pass


class NonExistentScreennames(Exception):
    pass


class ProtectedScreenname(Exception):
    pass


class ProtectedScreennames(Exception):
    pass


class TooManyFriends(Exception):
    pass


class FluidinfoParseError(Exception):
    pass


class FluidinfoNonexistentAttribute(Exception):
    pass


class FluidinfoPermissionDenied(Exception):
    pass


class FluidinfoError(Exception):
    pass


class Canceled(Exception):
    pass


def _ignoreHTTPStatus(fail, status):
    fail.trap(error.Error)
    if int(fail.value.status) != status:
        return fail


@defer.inlineCallbacks
def addUserByScreenname(cache, endpoint, userJob):
    # We must at least create the user.
    userJob.workToDo = WORK_TO_CREATE_A_FRIEND
    userJob.workDone = 0
    screenname = userJob.screenname
    log.msg('Adding user %r' % screenname)

    def catchUnknownScreenname(fail):
        fail.trap(error.Error)
        if int(fail.value.status) != http.NOT_FOUND:
            return fail
        return defer.fail(UnknownScreenname(screenname))

    def catchProtectedScreenname(fail):
        fail.trap(error.Error)
        if int(fail.value.status) != http.UNAUTHORIZED:
            return fail
        return defer.fail(ProtectedScreenname(screenname))

    d = cache.friendsIdCache[screenname]
    d.addErrback(catchUnknownScreenname)
    d.addErrback(catchProtectedScreenname)
    friendUids = yield d
    log.msg('Got %d friends for user %r' % (len(friendUids), screenname))

    # Make a tag for this new user to mark their friends with.
    ns = Namespace(TWITTER_USERNAME, TWITTER_FRIENDS_NAMESPACE_NAME)
    d = ns.createTag(endpoint, screenname.lower(),
        "A tag used to mark %s's Twitter friends." % screenname, False)
    # TODO: check the X-FluidDB-Error-Class header in the errback to make
    # sure it really got a namespace already exists error.
    d.addErrback(_ignoreHTTPStatus, http.PRECONDITION_FAILED)
    yield d
    # Note: the call to createTag (above) will return a Tag instance when
    # txFluidDB gets fixed.
    friendTag = Tag(TWITTER_USERNAME, TWITTER_FRIENDS_NAMESPACE_NAME,
                    screenname.lower())
    friendTagPath = friendTag.getPath()
    log.msg('Created Twitter friends tag %s' % friendTagPath)

    def _madeUserDone(userObject, user):
        userJob.workDone += WORK_TO_CREATE_A_FRIEND
        cache.extraTwitterTagsPool.add(
            addExtraTwitterTags(endpoint, userObject, user))
        return userObject

    def _madeUserErr(failure):
        userJob.workDone += WORK_TO_CREATE_A_FRIEND
        return failure

    def _tagFriendDone():
        userJob.workDone += WORK_TO_TAG_A_FRIEND

    def makeUser(user, thisIndex=None, totalToAdd=None):
        newName = user['screen_name']
        if thisIndex is not None:
            log.msg('Making user %r, friend %d/%d of %r.' %
                    (newName, thisIndex, totalToAdd, screenname))
        else:
            log.msg('Making user %r.' % newName)
        d = cache.oidUidScreennameCache.objectByUid(user['id'], newName)
        d.addCallbacks(_madeUserDone, _madeUserErr, callbackArgs=(user,))
        return d

    def _ignore404uid(fail, uid):
        fail.trap(error.Error)
        if int(fail.value.status) == http.NOT_FOUND:
            log.msg('Twitter uid %d is no longer found (404). Ignoring.' % uid)
            cache.userCache.removeUid(uid)
            cache.oidUidScreennameCache.removeUid(uid)
        else:
            log.msg('Failure fetching Twitter uid %d:' % uid)
            log.err(fail)

    def makeCreateUserJobs(friendsToAdd):
        nToAdd = len(friendsToAdd)
        for i, friendUid in enumerate(friendsToAdd):
            if userJob.canceled():
                log.msg('Detected cancelation of screenname %r.' % screenname)
                raise StopIteration
            d = cache.userCache.userByUid(friendUid)
            d.addCallbacks(makeUser, _ignore404uid,
                           callbackArgs=(i + 1, nToAdd),
                           errbackArgs=(friendUid,))
            yield d

    @defer.inlineCallbacks
    def addFriend(friendName, thisIndex, totalToAdd):
        log.msg('About to mark user %r as a friend %d/%d of %r.' %
                (friendName, thisIndex, totalToAdd, screenname))
        d = cache.oidUidScreennameCache.objectIdByScreenname(friendName)
        d.addErrback(log.err)
        objectId = yield d
        log.msg('Marking user %r as a friend %d/%d of %r' %
                (friendName, thisIndex, totalToAdd, screenname))
        if objectId is not None:
            o = Object(objectId)
            yield o.set(endpoint, friendTag, None)
            log.msg('Marked user %r as a friend %d/%d of %r' %
                    (friendName, thisIndex, totalToAdd, screenname))
        _tagFriendDone()

    def makeTagFriendsJobs():
        nFriendUids = len(friendUids)
        for i, friendUid in enumerate(friendUids):
            if userJob.canceled():
                log.msg('Detected cancelation of screenname %r.' % screenname)
                raise StopIteration
            d = cache.userCache.screennameByUid(friendUid)
            d.addCallbacks(addFriend, _ignore404uid,
                           callbackArgs=(i + 1, nFriendUids),
                           errbackArgs=(friendUid,))
            yield d

    # Get screename's id and add them as a Twitter user.
    user = yield cache.userCache.userByScreenname(screenname)
    userObject = yield makeUser(user)
    log.msg('User object for %r is %r' % (screenname, userObject))

    # Add the amount of work will it be to tag all friends.
    userJob.workToDo += (len(friendUids) * WORK_TO_TAG_A_FRIEND)

    # Figure out the work will it be to create whatever friends are needed.
    friendsToAdd = [fid for fid in friendUids
                    if not cache.oidUidScreennameCache.knownUid(fid)]
    nFriendsToAdd = len(friendsToAdd)
    log.msg('Must create %d new user objects as friends of %r.' %
            (nFriendsToAdd, screenname))

    if nFriendsToAdd and not userJob.canceled():
        userJob.workToDo += (nFriendsToAdd * WORK_TO_CREATE_A_FRIEND)
        start = time.time()

        # Create Fluidinfo objects for all the friends that we don't yet know
        # about.
        jobs = makeCreateUserJobs(friendsToAdd)
        deferreds = []
        coop = task.Cooperator()
        for i in xrange(MAX_SIMULTANEOUS_REQUESTS):
            d = coop.coiterate(jobs)
            d.addErrback(log.err)
            deferreds.append(d)
        yield defer.DeferredList(deferreds)

        if not userJob.canceled():
            elapsed = time.time() - start
            log.msg('Created %d new friend (of %r) objects in %.2f seconds. '
                    'Mean %.4f' % (nFriendsToAdd, screenname, elapsed,
                                   float(elapsed / nFriendsToAdd)))

    if friendUids and not userJob.canceled():
        # Tag all friends.
        start = time.time()
        jobs = makeTagFriendsJobs()
        deferreds = []
        coop = task.Cooperator()
        for i in xrange(MAX_SIMULTANEOUS_REQUESTS):
            d = coop.coiterate(jobs)
            d.addErrback(log.err)
            deferreds.append(d)
        log.msg('About to yield friend tagging DL for %r' % screenname)
        yield defer.DeferredList(deferreds)
        log.msg('Friend tagging DL finished for %r' % screenname)

        if not userJob.canceled():
            elapsed = time.time() - start
            nFriendsUids = len(friendUids)
            log.msg('Tagged %d objects as being a friend of %r in %.2f '
                    'seconds. Mean = %.4f' % (nFriendsUids, screenname,
                    elapsed, float(elapsed / nFriendsUids)))

    if userJob.canceled():
        log.msg('Canceled addUserByScreenname for %r.' % screenname)
        raise Canceled(screenname)
    else:
        # Add the updated tag to the user's object.
        log.msg('Adding updated tag to user object for %r' % screenname)
        yield userObject.set(endpoint, updatedTag, int(time.time()))
        log.msg('Successfully added screenname %r.' % (screenname,))

    userJob.workDone = userJob.workToDo


def friendOf(cache, endpoint, screenname1, screenname2):
    # Does the object for the user screenname2 have a screenname1
    # follows tag on it?

    def filter404(fail):
        fail.trap(error.Error)
        if int(fail.value.status) == http.NOT_FOUND:
            return False
        else:
            return fail

    def checkTagOnObject(objectId):
        o = Object(objectId)
        tag = Tag(TWITTER_USERNAME, TWITTER_FRIENDS_NAMESPACE_NAME,
                  screenname1.lower())
        d = o.get(endpoint, tag)
        d.addCallback(lambda _: True)
        return d

    d = cache.oidUidScreennameCache.objectIdByScreenname(screenname2)
    d.addCallback(checkTagOnObject)
    d.addErrback(filter404)
    return d


def intermediateQuery(cache, endpoint, queryTree):
    screennames = set()
    query.queryTreeExtractScreennames(queryTree, screennames)
    d = cache.userCache.usersByScreennames(screennames)
    d.addCallback(cb_intermediateQuery, screennames, cache, endpoint,
                  queryTree)
    return d


def cb_intermediateQuery(users, screennames, cache, endpoint, queryTree):
    # Make sure all users exist, that there were no other errors in
    # fetching them, and that none of them are protected.
    notFound = []
    otherError = []
    for name, user in users.items():
        if isinstance(user, failure.Failure):
            if user.check(error.Error):
                status = int(user.value.status)
                if status == http.NOT_FOUND:
                    notFound.append(name)
                else:
                    log.msg(user)
                    otherError.append(name)
            else:
                log.msg(user)
                otherError.append(name)
    if notFound:
        raise NonExistentScreennames(notFound)
    if otherError:
        raise ScreennameErrors(otherError)
    protected = [name for name in users if users[name]['protected']]
    if protected:
        raise ProtectedScreennames(protected)

    # Make sure to use defaults.FRIENDS_LIMIT here, not to import
    # that value. That's because we can change the value (in the
    # defaults module) using the admin interface.
    tooMany = [(name, users[name]['friends_count']) for name in users if
               (users[name]['friends_count'] > defaults.FRIENDS_LIMIT and
                not cache.adderCache.added(name))]
    if tooMany:
        raise TooManyFriends(tooMany)

    # Enqueue screennames of users that are not yet known.
    unknown = [name for name in users if not cache.adderCache.known(name)]
    if unknown:
        for name in unknown:
            cache.adderCache.put(name, users[name]['friends_count'])

    # Get the status of all the queried screennames.
    statusSummary = cache.adderCache.statusSummary(screennames)

    # Raise if not all queried screennames are added.
    if len(statusSummary['added']) != len(screennames):
        raise UnaddedScreennames(statusSummary)

    # We're good to go.
    queryStr = query.queryTreeToString(
        queryTree, TWITTER_USERNAME, TWITTER_FRIENDS_NAMESPACE_NAME)

    try:
        result = cache.queryCache.lookupQueryResult(queryStr)
    except KeyError:
        def _cacheResult(result, queryStr, cache, screennames):
            cache.queryCache.storeQueryResult(queryStr, result, screennames)
            return result
        log.msg('Cache miss on query %r.' % queryStr)
        d = Object.query(endpoint, queryStr)
        d.addCallback(lambda results: [r.uuid for r in results])
        d.addCallback(_cacheResult, queryStr, cache, screennames)
        return d
    else:
        log.msg('Query cache hit (size %d) for %r.' % (len(result), queryStr))
        return defer.succeed(result)

_fluidinfoErrors = {
    'TParseError': FluidinfoParseError,
    'TPathPermissionDenied': FluidinfoPermissionDenied,
    'TNonexistentAttribute': FluidinfoNonexistentAttribute,
    }


def _queryErr(fail, query):
    fail.trap(error.Error)
    errorClass = fail.value.response_headers.get('x-fluiddb-error-class')
    if errorClass is None:
        log.msg('No Fluidinfo error class header! '
                'Query %r got HTTP status %s' % (query, fail.value.status))
        raise FluidinfoError()
    else:
        errorClass = errorClass[0]

    try:
        log.msg('Error Class %r' % (errorClass,))
        raise _fluidinfoErrors[errorClass]()
    except KeyError:
        log.msg('Unhandled Fluidinfo error class %r Query %r got '
                'HTTP status %s' %
                (errorClass, query, fail.value.status))
        raise FluidinfoError()


def fluidinfoQuery(endpoint, query):
    d = Object.query(endpoint, query)
    d.addCallback(lambda results: [r.uuid for r in results])
    d.addErrback(_queryErr, query)
    return d


def simpleTweetURL(screennames, sortKey):
    return '%s?tab=%s&name1=%s&name2=%s&sort=%s' % (
        TICKERY_URL, tabName['simple'],
        urllib.quote(screennames[0].encode('utf-8')),
        urllib.quote(screennames[1].encode('utf-8')),
        sortKey)


def simpleUpdate(cookie, cookieDict, screennames, nUsers, sortKey, useAtSigns):
    for i, name in enumerate(screennames):
        if useAtSigns:
            if not name.startswith('@'):
                screennames[i] = '@' + name
        else:
            if name.startswith('@'):
                screennames[i] = name[1:]

    basic = '%s and %s follow %d people in common. See who: ' % (
        screennames[0], screennames[1], nUsers)
    url = simpleTweetURL(screennames, sortKey)

    if len(basic) + BITLY_URL_LEN + 1 + len(_hashTag) <= 140:
        text = '%s %s %s' % (basic, url, _hashTag)
    else:
        text = '%s %s' % (basic, url)
    return twitter.updateStatus(text, cookie, cookieDict)


def tweetURL(query, tabName, sortKey):
    return '%s?tab=%s&query=%s&sort=%s' % (
        TICKERY_URL, tabName, urllib.quote_plus(query.encode('utf-8')),
        sortKey)


def update(cookie, cookieDict, text, query, tabName, sortKey):
    url = tweetURL(query, tabName, sortKey)
    if len(text) + 1 + BITLY_URL_LEN + 1 + len(_hashTag) <= 140:
        text = '%s %s %s' % (text, url, _hashTag)
    else:
        text = '%s %s' % (text, url)
    return twitter.updateStatus(text, cookie, cookieDict)


def _lookupCookie(cookie, cache, fname):
    try:
        return cache.cookieCache[cookie]
    except KeyError:
        log.err('%s: Could not find cookie %r.' % (fname, cookie))
        raise terror.NoSuchCookie()


def follow(cookie, cache, endpoint, uid):
    user, _ = _lookupCookie(cookie, cache, 'follow')
    tag = Tag(TWITTER_USERNAME, TWITTER_FRIENDS_NAMESPACE_NAME,
              user['screen_name'].lower())
    d = cache.oidUidScreennameCache.objectByUid(
        uid, userNameCache=cache.userCache)
    d.addCallback(lambda o: o.set(endpoint, tag, None))
    # The logged in user may not yet exist in Fluidinfo.
    d.addErrback(_ignoreHTTPStatus, http.NOT_FOUND)
    return d


def unfollow(cookie, cache, endpoint, uid):
    user, _ = _lookupCookie(cookie, cache, 'unfollow')
    tag = Tag(TWITTER_USERNAME, TWITTER_FRIENDS_NAMESPACE_NAME,
              user['screen_name'].lower())
    d = cache.oidUidScreennameCache.objectByUid(
        uid, userNameCache=cache.userCache)
    d.addCallback(lambda o: o.delete(endpoint, tag))
    # The logged in user may not yet exist in Fluidinfo.
    d.addErrback(_ignoreHTTPStatus, http.NOT_FOUND)
    return d


def friendsIdFetcher(cookie, cache, screenname):
    # Note: only use the friends cache if the user is not protected. That's
    # because the cache only contains public users, to prevent people who
    # are not authorized followers of a private user from doing queries
    # on that person using our cache.
    #
    # We could still cache (elsewhere) the friends of private users, but
    # let's leave that for later, since most users are public and it's a
    # bit sensitive.
    user, accessToken = _lookupCookie(cookie, cache, 'friendsIdFetcher')
    if user['protected']:
        fetcher = twitter.FriendsIdFetcher(screenname, accessToken)
        d = fetcher.fetch()
    else:
        d = cache.friendsIdCache[screenname]
    return d


@defer.inlineCallbacks
def directAddUser(cache, screenname):
    # Make sure the user exists, that there are no errors in fetching them,
    # and that they are not protected.
    try:
        user = yield cache.userCache.userByScreenname(screenname)
    except error.Error, e:
        status = int(e.status)
        if status == http.NOT_FOUND:
            raise NonExistentScreennames('%s does not exist' % screenname)
        else:
            log.msg(e)
            raise ScreennameErrors(str(e))
    except:
        raise
    else:
        if user['protected']:
            raise ProtectedScreennames('%s is protected' % screenname)
        if cache.adderCache.added(screenname):
            raise Exception('%s is already added' % screenname)
        else:
            cache.adderCache.put(screenname, user['friends_count'])


@defer.inlineCallbacks
def bulkAddUsers(cache, screennames):
    # Add all users. Return a list of error messages.
    errs = []
    for screenname in screennames:
        try:
            user = yield cache.userCache.userByScreenname(screenname)
        except error.Error, e:
            status = int(e.status)
            if status == http.NOT_FOUND:
                errs.append('%r does not exist.' % screenname)
            else:
                errs.append('Error getting user %r: %s' % (screenname, e))
        else:
            if user['protected']:
                errs.append('%r is protected.' % screenname)
            elif user['friends_count'] > defaults.FRIENDS_LIMIT:
                errs.append('%r has too many friends (%d).' %
                        (screenname, user['friends_count']))
            elif cache.adderCache.added(screenname):
                errs.append('%r is already added.' % screenname)
            else:
                log.msg('Bulk add of %r.' % screenname)
                cache.adderCache.put(screenname, user['friends_count'])
    defer.returnValue(errs)


def addExtraTwitterTags(endpoint, userObject, user):
    # Add additional Twitter info tags to the user's object. We do this
    # asynchronously, and all taggings are launched at once (not
    # sequentially).  No-one is waiting on us, so we don't return anything.

    screenname = user['screen_name']

    def _err(failure, attr):
        log.err('Failed to add %s tag to user %r:' % (attr, screenname))
        log.err(failure)
        # Return None

    def _done(_):
        log.msg('Added extra tags to user %r.' % screenname)

    deferreds = []

    for attr, tag in extraTags.iteritems():
        d = userObject.set(endpoint, tag, user[attr])
        d.addErrback(_err, attr)
        deferreds.append(d)

    d = defer.DeferredList(deferreds)
    d.addCallback(_done)
    return d
