#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import re
import struct
import json
import argparse
import pokemon_pb2

from collections import OrderedDict
from datetime import datetime
from geopy.geocoders import GoogleV3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
LOGIN_URL = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'
PTC_CLIENT_SECRET = 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR'

SESSION = requests.session()
SESSION.headers.update({'User-Agent': 'Niantic App'})
SESSION.verify = False

DEBUG = True
COORDS_LATITUDE = 0
COORDS_LONGITUDE = 0
COORDS_ALTITUDE = 0

def f2i(float):
  return struct.unpack('<Q', struct.pack('<d', float))[0]

def f2h(float):
  return hex(struct.unpack('<Q', struct.pack('<d', float))[0])

def h2f(hex):
  return struct.unpack('<d', struct.pack('<Q', int(hex,16)))[0]

def set_location(location_name):
    geolocator = GoogleV3()
    loc = geolocator.geocode(location_name)

    print('[!] Your given location: {}'.format(loc.address))
    print('[!] lat/long/alt: {} {} {}'.format(loc.latitude, loc.longitude, loc.altitude))
    set_location_coords(loc.latitude, loc.longitude, loc.altitude)

def set_location_coords(lat, long, alt):
    global COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE
    COORDS_LATITUDE = f2i(lat)
    COORDS_LONGITUDE = f2i(long)
    COORDS_ALTITUDE = f2i(alt)

def get_location_coords():
    return (COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE)

def api_req(api_endpoint, access_token, req):
    try:
        p_req = pokemon_pb2.RequestEnvelop()
        p_req.unknown1 = 2
        p_req.rpc_id = 8145806132888207460

        p_req.requests.MergeFrom(req)

        p_req.latitude, p_req.longitude, p_req.altitude = get_location_coords()

        p_req.unknown12 = 989
        p_req.auth.provider = 'ptc'
        p_req.auth.token.contents = access_token
        p_req.auth.token.unknown13 = 59
        protobuf = p_req.SerializeToString()

        r = SESSION.post(api_endpoint, data=protobuf, verify=False)

        p_ret = pokemon_pb2.ResponseEnvelop()
        p_ret.ParseFromString(r.content)
        return p_ret
    except Exception,e:
        if DEBUG:
            print(e)
        return None


def get_api_endpoint(access_token):
    req = pokemon_pb2.RequestEnvelop()

    req1 = req.requests.add()
    req1.type = 2
    req2 = req.requests.add()
    req2.type = 126
    req3 = req.requests.add()
    req3.type = 4
    req4 = req.requests.add()
    req4.type = 129
    req5 = req.requests.add()
    req5.type = 5
    req5.message.unknown4 = "4a2e9bc330dae60e7b74fc85b98868ab4700802e"

    p_ret = api_req(API_URL, access_token, req.requests)

    try:
        return ('https://%s/rpc' % p_ret.api_url)
    except:
        return None


def get_profile(api_endpoint, access_token):
    req = pokemon_pb2.RequestEnvelop()

    req1 = req.requests.add()
    req1.type = 2

    return api_req(api_endpoint, access_token, req.requests)



def login_google(email,passw):
	reqses = requests.session()
	reqses.headers.update({'User-Agent':'Niantic App'})

	reqses.headers.update({'User-Agent':'Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143'})
	first='https://accounts.google.com/o/oauth2/auth?client_id=848232511240-73ri3t7plvk96pj4f85uj8otdat2alem.apps.googleusercontent.com&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code&scope=openid%20email%20https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email'
	second='https://accounts.google.com/AccountLoginInfo'
	third='https://accounts.google.com/signin/challenge/sl/password'
	last='https://accounts.google.com/o/oauth2/token'
	r=reqses.get(first)
	
	GALX= re.search('<input type="hidden" name="GALX" value=".*">',r.content)
	gxf= re.search('<input type="hidden" name="gxf" value=".*:.*">',r.content)
	cont = re.search('<input type="hidden" name="continue" value=".*">',r.content)
	
	GALX=re.sub('.*value="','',GALX.group(0))
	GALX=re.sub('".*','',GALX)
	
	gxf=re.sub('.*value="','',gxf.group(0))
	gxf=re.sub('".*','',gxf)
	
	cont=re.sub('.*value="','',cont.group(0))
	cont=re.sub('".*','',cont)
	
	data1={'Page':'PasswordSeparationSignIn',
			'GALX':GALX,
			'gxf':gxf,
			'continue':cont,
			'ltmpl':'embedded',
			'scc':'1',
			'sarp':'1',
			'oauth':'1',
			'ProfileInformation':'',
			'_utf8':'?',
			'bgresponse':'js_disabled',
			'Email':email,
			'signIn':'Next'}
	r1=reqses.post(second,data=data1)
	
	profile= re.search('<input id="profile-information" name="ProfileInformation" type="hidden" value=".*">',r1.content)
	gxf= re.search('<input type="hidden" name="gxf" value=".*:.*">',r1.content)

	gxf=re.sub('.*value="','',gxf.group(0))
	gxf=re.sub('".*','',gxf)
	
	profile=re.sub('.*value="','',profile.group(0))
	profile=re.sub('".*','',profile)

	data2={'Page':'PasswordSeparationSignIn',
			'GALX':GALX,
			'gxf':gxf,
			'continue':cont,
			'ltmpl':'embedded',
			'scc':'1',
			'sarp':'1',
			'oauth':'1',
			'ProfileInformation':profile,
			'_utf8':'?',
			'bgresponse':'js_disabled',
			'Email':email,
			'Passwd':passw,
			'signIn':'Sign in',
			'PersistentCookie':'yes'}
	r2=reqses.post(third,data=data2)
	fourth= r2.history[1].headers['Location'].replace('amp%3B','')
	r3=reqses.get(fourth)
	
	client_id=re.search('client_id=.*&from_login',fourth)
	client_id= re.sub('.*_id=','',client_id.group(0))
	client_id= re.sub('&from.*','',client_id)
	
	state_wrapper= re.search('<input id="state_wrapper" type="hidden" name="state_wrapper" value=".*">',r3.content)
	state_wrapper=re.sub('.*state_wrapper" value="','',state_wrapper.group(0))
	state_wrapper=re.sub('"><input type="hidden" .*','',state_wrapper)

	connect_approve=re.search('<form id="connect-approve" action=".*" method="POST" style="display: inline;">',r3.content)
	connect_approve=re.sub('.*action="','',connect_approve.group(0))
	connect_approve=re.sub('" me.*','',connect_approve)

	data3 = OrderedDict([('bgresponse', 'js_disabled'), ('_utf8', '☃'), ('state_wrapper', state_wrapper), ('submit_access', 'true')])
	r4=reqses.post(connect_approve.replace('amp;',''),data=data3)

	code= re.search('<input id="code" type="text" readonly="readonly" value=".*" style=".*" onclick=".*;" />',r4.content)
	code=re.sub('.*value="','',code.group(0))
	code=re.sub('" style.*','',code)

	data4={'client_id':client_id,
		'client_secret':'NCjF1TLi2CcY6t5mt0ZveuL7',
		'code':code,
		'grant_type':'authorization_code',
		'redirect_uri':'urn:ietf:wg:oauth:2.0:oob',
		'scope':'openid email https://www.googleapis.com/auth/userinfo.email'}
	r5 = reqses.post(last,data=data4)
	return json.loads(r5.content)['id_token']
	
	
def login_ptc(username, password):
    print('[!] login for: {}'.format(username))
    head = {'User-Agent': 'niantic'}
    r = SESSION.get(LOGIN_URL, headers=head)
    jdata = json.loads(r.content)
    data = {
        'lt': jdata['lt'],
        'execution': jdata['execution'],
        '_eventId': 'submit',
        'username': username,
        'password': password,
    }
    r1 = SESSION.post(LOGIN_URL, data=data, headers=head)

    ticket = None
    try:
        ticket = re.sub('.*ticket=', '', r1.history[0].headers['Location'])
    except Exception,e:
        if DEBUG:
            print(r1.json()['errors'][0])
        return None

    data1 = {
        'client_id': 'mobile-app_pokemon-go',
        'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
        'client_secret': PTC_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'code': ticket,
    }
    r2 = SESSION.post(LOGIN_OAUTH, data=data1)
    access_token = re.sub('&expires.*', '', r2.content)
    access_token = re.sub('.*access_token=', '', access_token)

    return access_token


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="PTC Username", required=True)
    parser.add_argument("-p", "--password", help="PTC Password", required=True)
    parser.add_argument("-l", "--location", help="Location", required=True)
    parser.add_argument("-g", "--google", help="Google Auth", action='store_true')
    parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')
    parser.add_argument("-s", "--client_secret", help="PTC Client Secret")
    parser.set_defaults(DEBUG=True)
    args = parser.parse_args()

    if args.debug:
        global DEBUG
        DEBUG = True
        print('[!] DEBUG mode on')

    if args.client_secret is not None:
        global PTC_CLIENT_SECRET
        PTC_CLIENT_SECRET = args.client_secret

    set_location(args.location)

    # Google Authentication
    if args.google:
        print('[+] Authentication with google...')
        access_token = login_google(args.username, args.password)
        print('[+] RPC Session Token: {} ...'.format(access_token[:25]))
    else:
        access_token = login_ptc(args.username, args.password)
        if access_token is None:
            print('[-] Wrong username/password')
            return
        print('[+] RPC Session Token: {} ...'.format(access_token[:25]))
    

    api_endpoint = get_api_endpoint(access_token)
    if api_endpoint is None:
        print('[-] RPC server offline')
        return
    print('[+] Received API endpoint: {}'.format(api_endpoint))

    profile = get_profile(api_endpoint, access_token)
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
