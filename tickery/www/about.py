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

from pyjamas.ui.HTML import HTML
from pyjamas.ui.Grid import Grid

body = """
<a href=\"http://fluidinfo.com\"><img src=\"fluidinfo.png\" \
class=\"about-logo\"/></a><h2>About Tickery</h2>

<p>

Tickery is a product of <a href=\"http://fluidinfo.com\">Fluidinfo</a>.
The name is a shortening of \"Twitter Query\".  We created Tickery partly
to provide a fun tool for exploring the world of <a
href=\"http://twitter.com\">Twitter</a> users. It lets you answer simple
but interesting questions about who Twitter users are following.  That
turns out to be a great way to discover new people to follow.

</p>

<p>

But there's a more important reason why we built Tickery: to
illustrate the flexibility and potential of
<a href=\"http://fluidinfo.com/fluiddb\">Fluidinfo</a>,
the underlying database.

</p>

<p>

Fluidinfo is quite different from traditional databases. What distinguishes
it most is its open approach to information control: anyone, or any
application, is always permitted to add information to any object in
Fluidinfo.

</p>

<p>

This means that <em>Tickery is completely open.</em> The Fluidinfo objects
that Tickery uses to hold information about Twitter users are yours to play
with too.  You can contribute additional information about Twitter users,
and can query on it (using the advanced tab). You can also build your own
applications that use Fluidinfo, exactly as Tickery does. Those applications
can search using the tags that Tickery has added, or on anything that you
or others might add.

</p>

<p>


With Fluidinfo, no one&mdash;not even you&mdash;has to anticipate your future
needs, and you never have to ask for permission to add new information. To
complement this openness at the highest-level, Fluidinfo has an underlying
identity and permissions system that ensures existing data can only be
accessed by the people and applications you choose.

</p>

<p>

At Fluidinfo, we believe it will one day be <em>much</em> easier to work
with information. We've built Fluidinfo to show you what we think the future
will look like. It's a future in which we'll work with information in more
flexible ways, and with data that is
<a href=\"http://blogs.fluidinfo.com/fluidinfo/2009/08/24/\
truly-social-data/\">truly social</a>.

</p>

<h3>Next</h3>

For details on how Tickery uses Fluidinfo to hold information on Twitter
users, read the help popup on the Advanced tab.  To learn more about how
Fluidinfo works, a good starting place is the <a
href=\"http://doc.fluidinfo.com/fluidDB/\">high-level description</a>.

To learn more about how we think about information, and what we're aiming
at with Fluidinfo, have a look at the <a
href=\"http://blogs.fluidinfo.com/fluidinfo\">Fluidinfo blog</a>. In
particular, following articles provide a good set of viewpoints:

<a href=\"http://blogs.fluidinfo.com/fluidinfo/2009/08/24/\
truly-social-data/\">Truly Social Data</a>,
<a href=\"http://blogs.fluidinfo.com/fluidinfo/2009/08/25/\
kaleidoscope-10-takes-on-fluiddb/\">Kaleidoscope: 10 Takes on Fluidinfo</a>,
<a href=\"http://blogs.fluidinfo.com/fluidinfo/2009/08/28/\
information-naturally/\">Information. Naturally.</a>,
<a href=\"http://blogs.fluidinfo.com/fluidinfo/2009/10/03/\
fluiddb-as-a-universal-metadata-engine/\">Fluidinfo as a Universal Metadata
Engine</a>,
<a href=\"http://blogs.fluidinfo.com/fluidinfo/2009/11/12/\
why-are-post-it-notes-sticky/\">Why are Post-It Notes Sticky?</a>,
and
<a href=\"http://blogs.fluidinfo.com/fluidinfo/2009/12/01/\
putting-metadata-onto-tweets-with-fluiddb/\">Putting Metadata onto Tweets
with Fluidinfo</a>.

<p>

If you'd like to use the Fluidinfo API, please <a
href=\"http://fluidinfo.com/accounts/new\">sign up</a>.

</p>

</p>
"""


class About(Grid):

    tabName = 'about'

    def __init__(self, topPanel):
        Grid.__init__(self, 1, 1, StyleName='about-panel')
        self.setWidget(0, 0, HTML(body, StyleName='about-body'))

    def addTopPanel(self):
        pass

    def onTimer(self, timerid):
        pass
