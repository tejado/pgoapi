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

import os
import re
import time
import base64
import random
import logging
import requests
import subprocess
import six

from google.protobuf import message

from importlib import import_module


import ctypes

from pgoapi.protobuf_to_dict import protobuf_to_dict
from pgoapi.exceptions import NotLoggedInException, ServerBusyOrOfflineException, ServerSideRequestThrottlingException, ServerSideAccessForbiddenException, UnexpectedResponseException, AuthTokenExpiredException, ServerApiEndpointRedirectException
from pgoapi.utilities import to_camel_case, get_time, get_format_time_diff, Rand48, long_to_bytes, generateLocation1, generateLocation2, generateRequestHash, f2i

from . import protos
from POGOProtos.Networking.Envelopes_pb2 import RequestEnvelope
from POGOProtos.Networking.Envelopes_pb2 import ResponseEnvelope
from POGOProtos.Networking.Requests_pb2 import RequestType
import Signature_pb2


class RpcApi:

    RPC_ID = 0
    START_TIME = 0

    def __init__(self, auth_provider, proxy_config=None):

        self.log = logging.getLogger(__name__)

        if proxy_config is not None:
            self._session.proxies = proxy_config

        self._auth_provider = auth_provider

        """ mystic unknown6 - revolved by PokemonGoDev """
        self._signature_gen = False
        self._signature_lib = None

        if RpcApi.START_TIME == 0:
            RpcApi.START_TIME = get_time(ms=True)

        if RpcApi.RPC_ID == 0:
            RpcApi.RPC_ID = int(random.random() * 10 ** 18)
            self.log.debug('Generated new random RPC Request id: %s', RpcApi.RPC_ID)

    def activate_signature(self, lib_path):
        try:
            self._signature_gen = True
            self._signature_lib = ctypes.cdll.LoadLibrary(lib_path)
        except:
            raise

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
            http_response = self._session.post(endpoint, data=request_proto_serialized, timeout=30)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            raise ServerBusyOrOfflineException(e)

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
        if isinstance(response_dict, dict):
            status_code = response_dict.get('status_code', None)
            if status_code == 102:
                raise AuthTokenExpiredException()
            elif status_code == 52:
                raise ServerSideRequestThrottlingException("Request throttled by server... slow down man")
            elif status_code == 53:
                api_url = response_dict.get('api_url', None)
                if api_url is not None:
                    exception = ServerApiEndpointRedirectException()
                    exception.set_redirected_endpoint(api_url)
                    raise exception
                else:
                    raise UnexpectedResponseException()

        return response_dict

    def check_authentication(self, response_dict):
        if isinstance(response_dict, dict) and ('auth_ticket' in response_dict) and \
           ('expire_timestamp_ms' in response_dict['auth_ticket']) and \
           (self._auth_provider.is_new_ticket(response_dict['auth_ticket']['expire_timestamp_ms'])):

            had_ticket = self._auth_provider.has_ticket()

            auth_ticket = response_dict['auth_ticket']
            self._auth_provider.set_ticket(
                [auth_ticket['expire_timestamp_ms'], base64.standard_b64decode(auth_ticket['start']), base64.standard_b64decode(auth_ticket['end'])])

            now_ms = get_time(ms=True)
            h, m, s = get_format_time_diff(now_ms, auth_ticket['expire_timestamp_ms'], True)

            if had_ticket:
                self.log.debug('Replacing old Session Ticket with new one valid for %02d:%02d:%02d hours (%s < %s)', h, m, s, now_ms, auth_ticket['expire_timestamp_ms'])
            else:
                self.log.debug('Received Session Ticket valid for %02d:%02d:%02d hours (%s < %s)', h, m, s, now_ms, auth_ticket['expire_timestamp_ms'])

    def _build_main_request(self, subrequests, player_position=None):
        self.log.debug('Generating main RPC request...')

        request = RequestEnvelope()
        request.status_code = 2
        request.request_id = self.get_rpc_id()

        if player_position is not None:
            request.latitude, request.longitude, request.altitude = player_position

        request.altitude = 8  # not as suspicious as 0

        """ generate sub requests before signature generation """
        request = self._build_sub_requests(request, subrequests)

        ticket = self._auth_provider.get_ticket()
        if ticket:
            self.log.debug('Found Session Ticket - using this instead of oauth token')
            request.auth_ticket.expire_timestamp_ms, request.auth_ticket.start, request.auth_ticket.end = ticket

            if self._signature_gen:
                ticket_serialized = request.auth_ticket.SerializeToString()

                sig = Signature_pb2.Signature()

                sig.location_hash1 = generateLocation1(ticket_serialized, request.latitude, request.longitude, request.altitude)
                sig.location_hash2 = generateLocation2(request.latitude, request.longitude, request.altitude)

                for req in request.requests:
                    hash = generateRequestHash(ticket_serialized, req.SerializeToString())
                    sig.request_hash.append(hash)

                sig.unk22 = os.urandom(32)
                sig.timestamp = get_time(ms=True)
                sig.timestamp_since_start = get_time(ms=True) - RpcApi.START_TIME

                signature_proto = sig.SerializeToString()

                u6 = request.unknown6.add()
                u6.request_type = 6
                u6.unknown2.unknown1 = self._generate_signature(signature_proto)
        else:
            self.log.debug('No Session Ticket found - using OAUTH Access Token')
            request.auth_info.provider = self._auth_provider.get_name()
            request.auth_info.token.contents = self._auth_provider.get_access_token()
            request.auth_info.token.unknown2 = 59

        # unknown stuff
        request.unknown12 = 989

        self.log.debug('Generated protobuf request: \n\r%s', request)

        return request

    def _generate_signature(self, signature_plain, lib_path="encrypt.so"):
        if self._signature_lib is None:
            self.activate_signature(lib_path)
        self._signature_lib.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_ubyte), ctypes.POINTER(ctypes.c_size_t)]
        self._signature_lib.restype = ctypes.c_int

        iv = os.urandom(32)

        output_size = ctypes.c_size_t()

        self._signature_lib.encrypt(signature_plain, len(signature_plain), iv, 32, None, ctypes.byref(output_size))
        output = (ctypes.c_ubyte * output_size.value)()
        self._signature_lib.encrypt(signature_plain, len(signature_plain), iv, 32, ctypes.byref(output), ctypes.byref(output_size))
        signature = b''.join(list(map(lambda x: six.int2byte(x), output)))
        return signature

    def _build_main_request_orig(self, subrequests, player_position=None):
        self.log.debug('Generating main RPC request...')

        request = RequestEnvelope()
        request.status_code = 2
        request.request_id = self.get_rpc_id()

        request = self._build_sub_requests(request, subrequests)

        if player_position is not None:
            request.latitude, request.longitude, request.altitude = player_position

        ticket = self._auth_provider.get_ticket()
        if ticket:
            self.log.debug('Found Session Ticket - using this instead of oauth token')
            request.auth_ticket.expire_timestamp_ms, request.auth_ticket.start, request.auth_ticket.end = ticket
        else:
            self.log.debug('No Session Ticket found - using OAUTH Access Token')
            request.auth_info.provider = self._auth_provider.get_name()
            request.auth_info.token.contents = self._auth_provider.get_access_token()
            request.auth_info.token.unknown2 = 59

        # unknown stuff
        request.unknown12 = 3352

        self.log.debug('Generated protobuf request: \n\r%s', request)

        return request

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

                for (key, value) in entry_content.items():
                    if isinstance(value, list):
                        self.log.debug("Found list: %s - trying as repeated", key)
                        for i in value:
                            try:
                                self.log.debug("%s -> %s", key, i)
                                r = getattr(subrequest_extension, key)
                                r.append(i)
                            except Exception as e:
                                self.log.warning('Argument %s with value %s unknown inside %s (Exception: %s)', key, i, proto_name, e)
                    elif isinstance(value, dict):
                        for k in value.keys():
                            try:
                                r = getattr(subrequest_extension, key)
                                setattr(r, k, value[k])
                            except Exception as e:
                                self.log.warning('Argument %s with value %s unknown inside %s (Exception: %s)', key, str(value), proto_name, e)
                    else:
                        try:
                            setattr(subrequest_extension, key, value)
                        except Exception as e:
                            try:
                                self.log.debug("%s -> %s", key, value)
                                r = getattr(subrequest_extension, key)
                                r.append(value)
                            except Exception as e:
                                self.log.warning('Argument %s with value %s unknown inside %s (Exception: %s)', key, value, proto_name, e)

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
        elif response_raw.status_code == 502:
            raise ServerBusyOrOfflineException("502: Bad Gateway")
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
            self.log.warning('Could not parse response: %s', e)
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

        if response_proto_dict.get('status_code', 1) == 53:
            exception = ServerApiEndpointRedirectException()
            exception.set_redirected_endpoint(response_proto_dict['api_url'])
            raise exception

        if 'returns' in response_proto_dict:
            del response_proto_dict['returns']

        list_len = len(subrequests_list)-1
        i = 0
        for subresponse in response_proto.returns:
            if i > list_len:
                self.log.info("Error - something strange happend...")

            request_entry = subrequests_list[i]
            if isinstance(request_entry, int):
                entry_id = request_entry
            else:
                entry_id = list(request_entry.items())[0][0]

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
