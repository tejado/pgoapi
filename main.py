#!/usr/bin/env python
import requests
import re
import json
import argparse
import pokemon_pb2
import settings
from api import api_req, get_api_endpoint
from login import login_google, login_ptc
from location import set_location

from datetime import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_profile(service, api_endpoint, access_token):
    req = pokemon_pb2.RequestEnvelop()

    req1 = req.requests.add()
    req1.type = 2

    return api_req(service, api_endpoint, access_token, req.requests)

def main():
    settings.init()
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--auth_service", help="Auth Service",
        required=True)
    parser.add_argument("-u", "--username", help="Username", required=True)
    parser.add_argument("-p", "--password", help="Password", required=True)
    parser.add_argument("-l", "--location", help="Location", required=True)
    parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')
    parser.add_argument("-s", "--client_secret", help="PTC Client Secret")
    parser.set_defaults(DEBUG=True)
    args = parser.parse_args()

    if args.auth_service not in ['ptc', 'google']:
      print('[!] Invalid Auth service specified')
      return

    if args.debug:
        settings.debug = True
        print('[!] DEBUG mode on')

    if args.client_secret is not None:
        global PTC_CLIENT_SECRET
        PTC_CLIENT_SECRET = args.client_secret

    set_location(args.location)

    if args.auth_service == 'ptc':
        access_token = login_ptc(args.username, args.password)
    else:
        access_token = login_google(args.username, args.password)

    if access_token is None:
        print('[-] Wrong username/password')
        return
    print('[+] RPC Session Token: {} ...'.format(access_token[:25]))

    api_endpoint = get_api_endpoint(args.auth_service, access_token)
    if api_endpoint is None:
        print('[-] RPC server offline')
        return
    print('[+] Received API endpoint: {}'.format(api_endpoint))

    profile = get_profile(args.auth_service, api_endpoint, access_token)
    if profile is not None:
        print('[+] Login successful')

        profile = profile.payload[0].profile
        print('[+] Username: {}'.format(profile.username))

        creation_time = datetime.fromtimestamp(int(profile.creation_time)/1000)
        print('[+] You are playing Pokemon Go since: {}'.format(
            creation_time.strftime('%Y-%m-%d %H:%M:%S'),
        ))

        print('[+] Poke Storage: {}'.format(profile.poke_storage))

        print('[+] Item Storage: {}'.format(profile.item_storage))

        for curr in profile.currency:
            print('[+] {}: {}'.format(curr.type, curr.amount))
    else:
        print('[-] Ooops...')


if __name__ == '__main__':
    main()
