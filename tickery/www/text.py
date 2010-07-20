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

from pyjamas.ui.TextArea import TextArea
from pyjamas.ui.TextBox import TextBox


class HighlightAll(object):

    def __init__(self):
        self.addFocusListener(self)

    def onFocus(self, sender):
        self.highlight()

    def highlight(self):
        self.selectAll()


class TextAreaFocusHighlight(TextArea, HighlightAll):

    def __init__(self, **kwargs):
        TextArea.__init__(self, **kwargs)
        HighlightAll.__init__(self)


class TextBoxFocusHighlight(TextBox, HighlightAll):

    def __init__(self, **kwargs):
        TextBox.__init__(self, **kwargs)
        HighlightAll.__init__(self)
