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

import re
import six
import logging
import requests

from . import __title__, __version__, __copyright__
from pgoapi.rpc_api import RpcApi
from pgoapi.auth_ptc import AuthPtc
from pgoapi.auth_google import AuthGoogle
from pgoapi.exceptions import AuthException, NotLoggedInException, ServerBusyOrOfflineException, NoPlayerPositionSetException, EmptySubrequestChainException

from . import protos
from POGOProtos.Networking.Requests_pb2 import RequestType

logger = logging.getLogger(__name__)

class PGoApi:

    def __init__(self):

        self.set_logger()

        self._auth_provider = None
        self._api_endpoint = 'https://pgorelease.nianticlabs.com/plfe/rpc'

        self._position_lat = None
        self._position_lng = None
        self._position_alt = None

        self.log.info('%s v%s - %s', __title__, __version__, __copyright__ )

    def set_logger(self, logger = None):
        self.log = logger or logging.getLogger(__name__)
        
    def get_api_endpoint(self):
        return self._api_endpoint

    def get_position(self):
        return (self._position_lat, self._position_lng, self._position_alt)

    def set_position(self, lat, lng, alt):
        self.log.debug('Set Position - Lat: %s Long: %s Alt: %s', lat, lng, alt)

        self._position_lat = lat
        self._position_lng = lng
        self._position_alt = alt
        
    def create_request(self):    
        request = PGoApiRequest(self._api_endpoint, self._auth_provider, self._position_lat, self._position_lng, self._position_alt)
        return request

    def __getattr__(self, func):
    
        def function(**kwargs):
            request = self.create_request()
            getattr(request, func)( _call_direct = True, **kwargs )
            return request.call()

        if func.upper() in  RequestType.keys():
            return function
        else:
            raise AttributeError
        
    def login(self, provider, username, password, lat = None, lng = None, alt = None, app_simulation = True):

        if lat and lng and alt:
            self._position_lat = lat
            self._position_lng = lng
            self._position_alt = alt

        if not isinstance(username, six.string_types) or not isinstance(password, six.string_types):
            raise AuthException("Username/password not correctly specified")

        if provider == 'ptc':
            self._auth_provider = AuthPtc()
        elif provider == 'google':
            self._auth_provider = AuthGoogle()
        else:
            raise AuthException("Invalid authentication provider - only ptc/google available.")

        self.log.debug('Auth provider: %s', provider)

        if not self._auth_provider.login(username, password):
            self.log.info('Login process failed')
            return False

        if app_simulation:
            self.log.info('Starting RPC login sequence (app simulation)')

            # making a standard call, like it is also done by the client
            request = self.create_request()

            request.get_player()
            request.get_hatched_eggs()
            request.get_inventory()
            request.check_awarded_badges()
            request.download_settings(hash="05daf51635c82611d1aac95c0b051d3ec088a930")

            response = request.call()
        else:
            self.log.info('Starting minimal RPC login sequence')
            response = self.get_player()

        if not response:
            self.log.info('Login failed!')
            return False

        if 'api_url' in response:
            self._api_endpoint = ('https://{}/rpc'.format(response['api_url']))
            self.log.debug('Setting API endpoint to: %s', self._api_endpoint)
        else:
            self.log.error('Login failed - unexpected server response!')
            return False

        if app_simulation:
            self.log.info('Finished RPC login sequence (app simulation)')
        else:
            self.log.info('Finished minimal RPC login sequence')

        self.log.info('Login process completed')

        return True
        

class PGoApiRequest:
    def __init__(self, api_endpoint, auth_provider, position_lat, position_lng, position_alt):
        self.log = logging.getLogger(__name__)

        """ Inherit necessary parameters """
        self._api_endpoint = api_endpoint
        self._auth_provider = auth_provider

        self._position_lat = position_lat
        self._position_lng = position_lng
        self._position_alt = position_alt

        self._req_method_list = []

    def call(self):
        if not self._req_method_list:
            raise EmptySubrequestChainException()
            
        if (self._position_lat is None) or (self._position_lng is None) or (self._position_alt is None):
            raise NoPlayerPositionSetException()

        if self._auth_provider is None or not self._auth_provider.is_login():
            self.log.info('Not logged in')
            return NotLoggedInException()

        request = RpcApi(self._auth_provider)

        self.log.info('Execution of RPC')
        response = None
        try:
            response = request.request(self._api_endpoint, self._req_method_list, self.get_position())
        except ServerBusyOrOfflineException as e:
            self.log.info('Server seems to be busy or offline - try again!')

        # cleanup after call execution
        self.log.info('Cleanup of request!')
        self._req_method_list = []

        return response

    def list_curr_methods(self):
        for i in self._req_method_list:
            print("{} ({})".format(RequestType.Name(i), i))

    def get_position(self):
        return (self._position_lat, self._position_lng, self._position_alt)

    def set_position(self, lat, lng, alt):
        self.log.debug('Set Position - Lat: %s Long: %s Alt: %s', lat, lng, alt)

        self._position_lat = lat
        self._position_lng = lng
        self._position_alt = alt

    def __getattr__(self, func):
        def function(**kwargs):

            if '_call_direct' in kwargs:
                del kwargs['_call_direct']
                self.log.info('Creating a new direct request...')
            elif not self._req_method_list:
                self.log.info('Creating a new request...')

            name = func.upper()
            if kwargs:
                self._req_method_list.append({RequestType.Value(name): kwargs})
                self.log.info("Adding '%s' to RPC request including arguments", name)
                self.log.debug("Arguments of '%s': \n\r%s", name, kwargs)
            else:
                self._req_method_list.append(RequestType.Value(name))
                self.log.info("Adding '%s' to RPC request", name)

            return self

        if func.upper() in  RequestType.keys():
            return function
        else:
            raise AttributeError
