#!/usr/bin/env python

import os
import sys
import fluidinfo
from urllib import quote

fluidinfo.login('twitter.com', os.environ['FLUIDINFO_TWITTER_PASSWORD'])

tags = sys.stdin.readlines()
ntags = len(tags)

for i, tag in enumerate(tags):
    tag = quote(tag[:-1])
    hdrs, response = fluidinfo.call('DELETE', '/tags/%s' % tag)
    if hdrs['status'] == '204':
        print '%d/%d deleted %s', (i + 1, ntags, tag)
    else:
        print '%d/%d failed deleting %s: %s' % (i + 1, ntags, tag, hdrs)
