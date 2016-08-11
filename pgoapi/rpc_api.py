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
import base64
import random
import logging
import requests
import subprocess

from google.protobuf import message

from importlib import import_module

from pgoapi.protobuf_to_dict import protobuf_to_dict
from pgoapi.exceptions import NotLoggedInException, ServerBusyOrOfflineException, ServerSideRequestThrottlingException, ServerSideAccessForbiddenException, UnexpectedResponseException
from pgoapi.utilities import f2i, h2f, to_camel_case, get_time_ms, get_format_time_diff

from . import protos
from POGOProtos.Networking.Envelopes_pb2 import RequestEnvelope
from POGOProtos.Networking.Envelopes_pb2 import ResponseEnvelope
from POGOProtos.Networking.Requests_pb2 import RequestType

class RpcApi:

    RPC_ID = 0

    def __init__(self, auth_provider):

        self.log = logging.getLogger(__name__)

        self._session = requests.session()
        self._session.headers.update({'User-Agent': 'Niantic App'})
        self._session.verify = True

        self._auth_provider = auth_provider

        if RpcApi.RPC_ID == 0:
            RpcApi.RPC_ID = int(random.random() * 10 ** 18)
            self.log.debug('Generated new random RPC Request id: %s', RpcApi.RPC_ID)

    def get_rpc_id(self):
        RpcApi.RPC_ID += 1
        self.log.debug("Incremented RPC Request ID: %s", RpcApi.RPC_ID)

        return RpcApi.RPC_ID

    def decode_raw(self, raw):
        output = error = None
        try:
            process = subprocess.Popen(['protoc', '--decode_raw'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
            output, error = process.communicate(raw)
        except:
            output = "Couldn't find protoc in your environment OR other issue..."

        return output

    def get_class(self, cls):
        module_, class_ = cls.rsplit('.', 1)
        class_ = getattr(import_module(module_), class_)
        return class_

    def _make_rpc(self, endpoint, request_proto_plain):
        self.log.debug('Execution of RPC')

        request_proto_serialized = request_proto_plain.SerializeToString()
        try:
            http_response = self._session.post(endpoint, data=request_proto_serialized)
        except requests.exceptions.ConnectionError as e:
            raise ServerBusyOrOfflineException

        return http_response

    def request(self, endpoint, subrequests, player_position):

        if not self._auth_provider or self._auth_provider.is_login() is False:
            raise NotLoggedInException()

        request_proto = self._build_main_request(subrequests, player_position)
        response = self._make_rpc(endpoint, request_proto)

        response_dict = self._parse_main_response(response, subrequests)

        self.check_authentication(response_dict)

        """ 
        some response validations 
        """
        if isinstance(response_dict, dict) and 'status_code' in response_dict:
            sc = response_dict['status_code']
            if sc == 102:
                raise NotLoggedInException()
            elif sc == 52:
                raise ServerSideRequestThrottlingException("Request throttled by server... slow down man")

        return response_dict

    def check_authentication(self, response_dict):
        if isinstance(response_dict, dict) and ('auth_ticket' in response_dict) and \
           ('expire_timestamp_ms' in response_dict['auth_ticket']) and \
           (self._auth_provider.is_new_ticket(response_dict['auth_ticket']['expire_timestamp_ms'])):

            had_ticket = self._auth_provider.has_ticket()

            auth_ticket = response_dict['auth_ticket']
            self._auth_provider.set_ticket(
                [auth_ticket['expire_timestamp_ms'], base64.standard_b64decode(auth_ticket['start']), base64.standard_b64decode(auth_ticket['end'])])

            now_ms = get_time_ms()
            h, m, s = get_format_time_diff(now_ms, auth_ticket['expire_timestamp_ms'], True)

            if had_ticket:
                self.log.debug('Replacing old auth ticket with new one valid for %02d:%02d:%02d hours (%s < %s)', h, m, s, now_ms, auth_ticket['expire_timestamp_ms'])
            else:
                self.log.debug('Received auth ticket valid for %02d:%02d:%02d hours (%s < %s)', h, m, s, now_ms, auth_ticket['expire_timestamp_ms'])

    def _build_main_request(self, subrequests, player_position = None):
        self.log.debug('Generating main RPC request...')

        request = RequestEnvelope()
        request.status_code = 2
        request.request_id = self.get_rpc_id()

        if player_position is not None:
            request.latitude, request.longitude, request.altitude = player_position

        ticket = self._auth_provider.get_ticket()
        if ticket:
            self.log.debug('Found auth ticket - using this instead of oauth token')
            request.auth_ticket.expire_timestamp_ms, request.auth_ticket.start, request.auth_ticket.end = ticket
        else:
            self.log.debug('NO auth ticket found - using oauth token')
            request.auth_info.provider = self._auth_provider.get_name()
            request.auth_info.token.contents = self._auth_provider.get_token()
            request.auth_info.token.unknown2 = 59

        # unknown stuff
        request.unknown12 = 989

        request = self._build_sub_requests(request, subrequests)

        self.log.debug('Generated protobuf request: \n\r%s', request )

        return request

    def _parse_list(self, values, message):
        if isinstance(values[0], dict): # values need to be further parsed
            for v in values:
                sub = message.add()
                self._parse_dict(v, sub)
        else:
            message.extend(values)

    def _parse_dict(self, values, message):
        for k,v in values.iteritems():
            if isinstance(v, dict): # needs further breakdown
                self._parse_dict(v, getattr(message, k))
            elif isinstance(v, list):
                self._parse_list(v, getattr(message, k))
            else:
                try:
                    setattr(message, k, v)
                except AttributeError:
                    self.log.error('Accessing Invalid Attribute %r.%r = %r', message, k, v)

    def _build_sub_requests(self, mainrequest, subrequest_list):
        self.log.debug('Generating sub RPC requests...')

        for entry in subrequest_list:
            if isinstance(entry, dict):

                entry_id = list(entry.items())[0][0]
                entry_content = entry[entry_id]

                entry_name = RequestType.Name(entry_id)

                proto_name = to_camel_case(entry_name.lower()) + 'Message'
                proto_classname = 'POGOProtos.Networking.Requests.Messages_pb2.' + proto_name
                subrequest_extension = self.get_class(proto_classname)()

                self.log.debug("Subrequest class: %s", proto_classname)

                self._parse_dict(entry_content, subrequest_extension)
                
                subrequest = mainrequest.requests.add()
                subrequest.request_type = entry_id
                subrequest.request_message = subrequest_extension.SerializeToString()

            elif isinstance(entry, int):
                subrequest = mainrequest.requests.add()
                subrequest.request_type = entry
            else:
                raise Exception('Unknown value in request list')

        return mainrequest


    def _parse_main_response(self, response_raw, subrequests):
        self.log.debug('Parsing main RPC response...')

        if response_raw.status_code == 403:
            raise ServerSideAccessForbiddenException("Seems your IP Address is banned or something else went badly wrong...")
        elif response_raw.status_code != 200:
            error = 'Unexpected HTTP server response - needs 200 got {}'.format(response_raw.status_code)
            self.log.warning(error)
            self.log.debug('HTTP output: \n%s', response_raw.content.decode('utf-8'))
            raise UnexpectedResponseException(error)

        if response_raw.content is None:
            self.log.warning('Empty server response!')
            return False

        response_proto = ResponseEnvelope()
        try:
            response_proto.ParseFromString(response_raw.content)
        except message.DecodeError as e:
            self.log.warning('Could not parse response: %s', str(e))
            return False

        self.log.debug('Protobuf structure of rpc response:\n\r%s', response_proto)
        try:
            self.log.debug('Decode raw over protoc (protoc has to be in your PATH):\n\r%s', self.decode_raw(response_raw.content).decode('utf-8'))
        except:
            self.log.debug('Error during protoc parsing - ignored.')

        response_proto_dict = protobuf_to_dict(response_proto)
        response_proto_dict = self._parse_sub_responses(response_proto, subrequests, response_proto_dict)

        return response_proto_dict

    def _parse_sub_responses(self, response_proto, subrequests_list, response_proto_dict):
        self.log.debug('Parsing sub RPC responses...')
        response_proto_dict['responses'] = {}

        if 'returns' in response_proto_dict:
            del response_proto_dict['returns']

        list_len = len(subrequests_list) -1
        i = 0
        for subresponse in response_proto.returns:
            if i > list_len:
                self.log.info("Error - something strange happend...")

            request_entry = subrequests_list[i]
            if isinstance(request_entry, int):
                entry_id = request_entry
            else:
                entry_id =  list(request_entry.items())[0][0]

            entry_name = RequestType.Name(entry_id)
            proto_name = to_camel_case(entry_name.lower()) + 'Response'
            proto_classname = 'POGOProtos.Networking.Responses_pb2.' + proto_name

            self.log.debug("Parsing class: %s", proto_classname)

            subresponse_return = None
            try:
                subresponse_extension = self.get_class(proto_classname)()         
            except Exception as e:
                subresponse_extension = None
                error = 'Protobuf definition for {} not found'.format(proto_classname)
                subresponse_return = error
                self.log.debug(error)

            if subresponse_extension:
                try: 
                    subresponse_extension.ParseFromString(subresponse)
                    subresponse_return = protobuf_to_dict(subresponse_extension)
                except:
                    error = "Protobuf definition for {} seems not to match".format(proto_classname)
                    subresponse_return = error
                    self.log.debug(error)

            response_proto_dict['responses'][entry_name] = subresponse_return
            i += 1

        return response_proto_dict
