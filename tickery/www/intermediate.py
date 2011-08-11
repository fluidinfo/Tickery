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
import defaults

from pyjamas.ui.HTML import HTML

_instructions = """
<p>

Using the intermediate tab you can ask interesting questions about Twitter
friends.  In the text-entry area, enter a query using Twitter user names to
represent the set of their friends (the people they follow).

</p><p>

Writing queries is very easy:

<ul>
<li>

The simplest query is just a user name. E.g.,
<a href=\"%(intq)sjack\">jack</a>, will list jack's friends.

</li>
<li>

Use <span class=\"example\">and</span> to get friends in common.  This is
what the simple tab provides, limited to queries with just two names, like
<a href=\"%(intq)sjack+and+ev\">jack and ev</a>. On the intermediate tab
you can use more names, e.g., <a href=\"%(intq)sjack+and+ev+and+biz\">jack
and ev and biz</a>.

</li>
<li>

Similarly, you can use <span class=\"example\">or</span> to get friends of
either user. E.g., <a href=\"%(intq)sjack+or+ev\">jack or ev</a> will
return users who are friends of jack or of ev (or both).

</li>
<li>

You can use <span class=\"example\">except</span> to exclude a set of
friends. E.g., <a href=\"%(intq)sjack+except+ev\">jack except ev</a> shows
users that jack follows but who ev does not.

</li>
<li>

Finally, parentheses can be used for grouping where necessary. E.g., <a
href=\"%(intq)sjack+except+(ev+or+biz)\">jack except (ev or biz)</a> will
get you the people jack is following, except those that either of ev or biz
is following.

</ul>
</p>

<h3 class=\"huh-h3\">Advanced Tips</h3>

<p>

You can abbreviate
<span class=\"example\">or</span>,
<span class=\"example\">and</span>, and
<span class=\"example\">except</span>, to the symbols
<span class=\"example\">|</span>,
<span class=\"example\">&amp;</span>, and
<span class=\"example\">-</span>.

</p>

<p>

Operator precedence, from low to high, is <span class=\"example\">or</span>,
<span class=\"example\">and</span>,
<span class=\"example\">except</span>. So, for example,
<span class=\"example\">A and B except C or D</span> is interpreted as
<span class=\"example\">(A and (B except C)) or D</span>.

</p>

<p>

If you prefer, you can prefix user names with an <span
class=\"example\">@</span> symbol. If your Twitter user name happens to be
<span class=\"example\">or</span>, or <span class=\"example\">and</span>,
or <span class=\"example\">except</span>, you will find this helpful :-)
E.g., <a href=\"%(intq)s@except+or+@and\">@except or @and</a>.

</p>

""" % {
    'intq': '%s/?tab=intermediate&query=' % defaults.TICKERY_URL,
}


class Intermediate(LargeQueryTab):
    tabName = 'intermediate'
    defaultQuery = 'jack and ev except biz'

    def __init__(self, topPanel):
        self.goButtonRemoteMethod = 'intermediateQuery'
        self.instructions = HTML(_instructions)
        self.instructionsTitle = 'Simple queries using the intermediate tab'
        LargeQueryTab.__init__(self, topPanel)
