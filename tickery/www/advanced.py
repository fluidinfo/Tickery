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

from tickerytab import LargeQueryTab
import simple, defaults

from pyjamas.ui.HTML import HTML

_instructions = """
<h3 class=\"huh-h3\">Exposing FluidDB</h3>

<p>

Tickery stores information on Twitter users in
<a href=\"http://fluidinfo.com/fluiddb\">FluidDB</a>. 

The simple and intermediate tabs just provide convenient&mdash;but also
constrained&mdash;query interfaces to FluidDB. The advanced tab takes the
gloves off, letting you interact with <a
href=\"http://fluidinfo.com/fluiddb\">FluidDB</a> using its native query
language. Though the native query language is a little more verbose, there
are <span class=\"instructions-em\">many</span> interesting possibilities
when you can search on anything you like.

</p><p>

Why FluidDB and not just a traditional database? Part of the answer is that
FluidDB allows anyone to add new data. You can query on that too, right
here on the advanced tab.

</p>

<h3 class=\"huh-h3\">The FluidDB query language</h3>

<p>

FluidDB stores a tagged object for each Twitter user that Tickery knows
about.  The query language is designed to match objects based on the
presence of tags, and their values.  Let's first see what happens behind
the scenes on the simple and intermediate tabs.

</p><p>

On the simple tab, querying with user names <span
class=\"example\">%(simpleUser1)s</span> and <span
class=\"example\">%(simpleUser2)s</span> results in the query

<a href=\"%(advancedq)shas+%(friends)s/%(simpleUser1)s+and+has+%(friends)s/%(simpleUser2)s\">has %(friends)s/%(simpleUser1)s and has %(friends)s/%(simpleUser2)s</a>

being sent to FluidDB. I.e., Tickery asks FluidDB for all objects that have
a <span class=\"example\">%(friends)s/%(simpleUser1)s</span> tag and also a
<span class=\"example\">%(friends)s/%(simpleUser2)s</span> tag.

</p><p>

On the intermediate tab, queries are also translated directly into FluidDB
queries. For example, the query

<a href=\"%(intq)sbiz+except+ev\">biz except ev</a>

results in the FluidDB query:

<a href=\"%(advancedq)shas+%(friends)s/biz+except+has+%(friends)s/ev\">has %(friends)s/biz except has %(friends)s/ev</a>.

That is, Tickery asks FluidDB for all objects that have a
<span class=\"example\">%(friends)s/biz</span>
tag,
<span class=\"example\">except</span>
those that also have a
<span class=\"example\">%(friends)s/ev</span>
tag.

</p><p>

Try the above links and you'll see the expected results.

</p>

<h3 class=\"huh-h3\">What's new?</h3>

<p>

The FluidDB objects matching the above queries all also have <span
class=\"example\">twitter.com/users/screen_name</span> and <span
class=\"example\">twitter.com/users/id</span> tags, which Tickery uses to
help display its results.

</p><p>

You can query on those tags directly in the advanced tab. For example, we
can find people with a low Twitter id via

<a href=\"%(advancedq)stwitter.com/users/id<100\">twitter.com/users/id <
100</a>, or we can look for a particular user:

<a href='%(advancedq)stwitter.com/users/screen_name+=+\"%(simpleUser1)s\"'>twitter.com/users/screen_name = \"%(simpleUser1)s\"</a>. FluidDB has some other
Twitter tags on its objects too. For example, you can query

<a href='%(advancedq)stwitter.com/users/followers_count+>+100000'>twitter.com/users/followers_count > 100000</a>.

<p/>

<h3 class=\"huh-h3\">Diversity</h3>

<p>

But that's not all. In fact, it's only the beginning.

</p><p>

Because FluidDB objects can be added to by anyone, we can query on tags
that were added by other people and that have nothing to do with
Twitter. For example, my user name in both FluidDB and Twitter is <span
class=\"example\">terrycojones</span>. I've added a <span
class=\"example\">terrycojones/met</span> tag to FluidDB's objects for
Twitter people that I've met in person. So the query

<a href='%(advancedq)shas+%(friends)s/terrycojones+and+has+terrycojones/met'>has %(friends)s/terrycojones and has terrycojones/met</a>

shows the Twitter people I follow that I have also met, while

<a href='%(advancedq)shas+%(friends)s/terrycojones+except+has+terrycojones/met'>has %(friends)s/terrycojones except has terrycojones/met</a>

shows those I have not met.

</p><p>

The possibilities here are literally endless. They get interesting
rapidly, even with just a couple of extra tags in the mix.  For example,
the other FluidDB programmer, Esteve, has also added <span
class=\"example\">esteve/met</span> tags to the people he follows and has
met. The query

<a href='%(advancedq)s(has+%(friends)s/terrycojones+and+has+%(friends)s/esteve)+except+(has+terrycojones/met+or+has+esteve/met)'>(has %(friends)s/terrycojones and has %(friends)s/esteve) except (has terrycojones/met or has esteve/met)</a>

shows people we both follow but which neither of us has met. And

<a href='%(advancedq)s(has+%(friends)s/esteve+and+has+terrycojones/met)+except+has+esteve/met'>(has %(friends)s/esteve and has terrycojones/met) except has esteve/met</a>

shows people Esteve follows that I have met in person but whom he has
not&mdash;we could use this, and its complement, to figure out who we
should introduce each other to. Imagine the additional richness we could
extract from Twitter if someone wrote e.g., a Firefox extension that simply
let you click to indicate which of the people you follow you've also met.
And that's just one additional tag in FluidDB. It's easy to dream up many
others.

</p>

<h3 class=\"huh-h3\">How to join in</h3>

<p>

The best part of all this is that you can play too.

The most important thing to understand about the underlying FluidDB objects
is that while their tags have owners and permissions, the objects
themselves do not. So you can use the FluidDB API

(<a href=\"http://doc.fluidinfo.com/fluidDB/index.html\">description</a>,
<a href=\"http://doc.fluidinfo.com/fluidDB/api/index.html\">details</a>)

to add any tags you like to FluidDB objects, <span
class=\"instructions-em\">including the objects that Tickery has
tagged</span>, and you can query on them in any combination.

</p>

<p>

If you'd like to use the FluidDB API, please <a
href=\"http://fluidinfo.com/accounts/new\">reserve a FluidDB username</a>
and then <a href=\"mailto:api@fluidinfo.com\">send us mail</a> to get a
password.  Note that FluidDB is still in an early <a
href=\"http://blogs.fluidinfo.com/fluidDB/2009/08/17/a-private-alpha-launch/\">private alpha</a> phase.

</p>

""" % {
    'simpleUser1' : simple._defaultName1,
    'simpleUser2' : simple._defaultName2,
    'friends' : '%s/%s' % (defaults.TWITTER_USERNAME,
                           defaults.TWITTER_FRIENDS_NAMESPACE_NAME),
    'intq' : '%s/?tab=intermediate&query=' % defaults.TICKERY_URL,
    'advancedq' : '%s/?tab=advanced&query=' % defaults.TICKERY_URL,
}



class Advanced(LargeQueryTab):

    tabName = 'advanced'

    defaultQuery = (
        '''has %(tw)s/%(fr)s/jack and has %(tw)s/%(fr)s/ev''' %
        { 'tw' : 'twitter.com', 'fr' : 'friends', })

    def __init__(self, topPanel):
        self.goButtonRemoteMethod = 'fluidDBQuery'
        self.instructions = HTML(_instructions)
        self.instructionsTitle = 'The FluidDB query language & the advanced tab'
        LargeQueryTab.__init__(self, topPanel)
