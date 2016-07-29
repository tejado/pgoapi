"""
pgoapi - Pokemon Go API
Copyright (c) 2016 tjado <https://github.com/tejado>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
OR OTHER DEALINGS IN THE SOFTWARE.

Author: tjado <https://github.com/tejado>
"""

from __future__ import absolute_import

import logging
from pgoapi.utilities import get_time_ms, get_format_time_diff

class Auth:

    def __init__(self):
        self.log = logging.getLogger(__name__)

        self._auth_provider = None

        self._login = False
        self._auth_token = None

        self._ticket_expire = None
        self._ticket_start = None
        self._ticket_end = None

    def get_name(self):
        return self._auth_provider

    def is_login(self):
        return self._login

    def get_token(self):
        return self._auth_token

    def has_ticket(self):
        if self._ticket_expire and self._ticket_start and self._ticket_end:
            return True
        else:
            return False

    def set_ticket(self, params):
        self._ticket_expire, self._ticket_start, self._ticket_end = params

    def is_new_ticket(self, new_ticket_time_ms):
        if self._ticket_expire is None or new_ticket_time_ms > self._ticket_expire:
            return True
        else:
            return False

    def check_ticket(self):
        if self.has_ticket():
            now_ms = get_time_ms()
            if now_ms < (self._ticket_expire - 10000):
                h, m, s = get_format_time_diff(now_ms, self._ticket_expire, True)
                self.log.debug('Auth ticket still valid for further %02d:%02d:%02d hours (%s < %s)', h, m, s, now_ms, self._ticket_expire)
                return True
            else:
                self.log.debug('Removed expired auth ticket (%s < %s)', now_ms, self._ticket_expire)
                self._ticket_expire, self._ticket_start, self._ticket_end = (None, None, None)
                return False
        else:
            return False

    def get_ticket(self):
        if self.check_ticket():
            return (self._ticket_expire, self._ticket_start, self._ticket_end)
        else:
            return False

    def login(self, username, password):
        raise NotImplementedError()