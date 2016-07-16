import requests
import re
import struct
import json
import argparse
import pokemon_pb2
import time

from google.protobuf.internal import encoder

from datetime import datetime
from geopy.geocoders import GoogleV3
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from s2sphere import *

def encode(cellid):
    output = []
    encoder._VarintEncoder()(output.append, cellid)
    return ''.join(output)

def getNeighbors():
    origin = CellId.from_lat_lng(LatLng.from_degrees(FLOAT_LAT, FLOAT_LONG)).parent(15)
    walk = [origin.id()]
    # 10 before and 10 after
    next = origin.next()
    prev = origin.prev()
    for i in range(10):
        walk.append(prev.id())
        walk.append(next.id())
        next = next.next()
        prev = prev.prev()
    return walk



API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'
LOGIN_URL = 'https://sso.pokemon.com/sso/login?service=https%3A%2F%2Fsso.pokemon.com%2Fsso%2Foauth2.0%2FcallbackAuthorize'
LOGIN_OAUTH = 'https://sso.pokemon.com/sso/oauth2.0/accessToken'

SESSION = requests.session()
SESSION.headers.update({'User-Agent': 'Niantic App'})
SESSION.verify = False

DEBUG = True
COORDS_LATITUDE = 0
COORDS_LONGITUDE = 0
COORDS_ALTITUDE = 0
FLOAT_LAT = 0
FLOAT_LONG = 0

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
    global FLOAT_LAT, FLOAT_LONG
    FLOAT_LAT = lat
    FLOAT_LONG = long
    COORDS_LATITUDE = f2i(lat) # 0x4042bd7c00000000 # f2i(lat)
    COORDS_LONGITUDE = f2i(long) # 0xc05e8aae40000000 #f2i(long)
    COORDS_ALTITUDE = f2i(alt)

def get_location_coords():
    return (COORDS_LATITUDE, COORDS_LONGITUDE, COORDS_ALTITUDE)

def api_req(api_endpoint, access_token, *mehs, **kw):
    try:
        p_req = pokemon_pb2.RequestEnvelop()
        p_req.rpc_id = 1469378659230941192

        p_req.unknown1 = 2

        p_req.latitude, p_req.longitude, p_req.altitude = get_location_coords()

        p_req.unknown12 = 989

        if 'useauth' not in kw:
            p_req.auth.provider = 'ptc'
            p_req.auth.token.contents = access_token
            p_req.auth.token.unknown13 = 14
        else:
            p_req.unknown11.unknown71 = kw['useauth'].unknown71
            p_req.unknown11.unknown72 = kw['useauth'].unknown72
            p_req.unknown11.unknown73 = kw['useauth'].unknown73

        for meh in mehs:
            p_req.MergeFrom(meh)



        print("Request:")
        print(p_req)
        print('')

        protobuf = p_req.SerializeToString()

        r = SESSION.post(api_endpoint, data=protobuf, verify=False)

        p_ret = pokemon_pb2.ResponseEnvelop()
        p_ret.ParseFromString(r.content)

        print("Response:")
        print(p_ret)
        print("\n\n")

        return p_ret
    except Exception, e:
        if DEBUG:
            print(e)
        return None

def get_second_profile(access_token, api, useauth, message, *reqq):
    req = pokemon_pb2.RequestEnvelop()

    req1 = req.requests.add()
    req1.type = 2
    if len(reqq) >= 1:
        req1.MergeFrom(reqq[0])

    req2 = req.requests.add()
    req2.type = 126
    if len(reqq) >= 2:
        req2.MergeFrom(reqq[1])

    req3 = req.requests.add()
    req3.type = 4
    if len(reqq) >= 3:
        req3.MergeFrom(reqq[2])

    req4 = req.requests.add()
    req4.type = 129
    if len(reqq) >= 4:
        req4.MergeFrom(reqq[3])

    req5 = req.requests.add()
    req5.type = 5
    if len(reqq) >= 5:
        req5.MergeFrom(reqq[4])


    req.unknown6.unknown1 = 6
    req.unknown6.unknown2.unknown1 = message
    # req5.message.unknown4 = "4a2e9bc330dae60e7b74fc85b98868ab4700802e"

    return api_req(api, access_token, req, useauth = useauth)

def get_profile(access_token, api):
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

    req.unknown6.unknown1 = 6
    req.unknown6.unknown2.unknown1 = "\250\251\t\3553\343\320S\305,\226\250>\334\240\032^\211g\221T\3120B\345\026Ia5\312\341\363\314E\006\301\320\376\206d\266F\032x\031DW9w\241\320a\333\242\215f\244v\266\222\221\247q]s\330`r\364\000O\265Y\267\374\203\325\t\215\363\002G\273\337\035\217p\237\205\304:3h^\256\214\252\327fr\357\300\325P)\023{\326\367)s3Ul\340$\2219*\263ut\327\373\375\002\232\t\323\343zS\362\255\003\002>\202\361\2646\326\261\352\032\363\374\217\223EA\333\340-\245!\327C\314.\016\227\330\0369\373\322J,\301\264KV\006\336\374w5>\241\311Z*\371\320Y.\341,\206\347fR\345\246\352\023\302\022\201\\\tG\355 \260\330\000\331\217\\&\232n\375\214\340%\031m\300\267\222@@\227\304\3138\321uw6nJ\241\245/O[\351x6@(\242\264C\363\270,\005\212\262\351\312\304\275;hs&,\005\340\340u\314kMm\211\'\2511\254\333-P7\022\236i\020\2101\247\344>u\005\n\213\307\2313\302F\267\322\210v\006\030\333\023&\357)=\301\2317\244\224@jn\324}\241\344\3250\202J\313\225\233I\237\035\v*.\342 Z\275,\241\273\022F\375\\\202~\372^\004\373\216\rru\273\305b\262\346\314 \363\260\224\325\260e\357\366\347\n\025\"R\342Hb\313\211n@y\034\316\203y\341\266\314` \377\020\236\252\247\2222\231\004\b\262\f\305PJ\333\276p\353\"\272\322\213Y\271\377c\212\227\230+\322$g\375\261\025\2770\227L)\327\237\255\300i\243\261\231\300\274\020\333\270\346T\252h\035Y\326\020\f\270\\\376\223\307\227C\016L\ag\020\333&\222o\366\242\366p\3373\230\266\351\373]|\334\210\376p\331\203\322t\200\365\365\214V\225{\315\203tv\307\356\035\003\221\204w\026\024Z\250\331\373\245\300h\336V\206\344R+\0031\373\263\317V\350\327\001\273UnM\026\001o\371"

    # req5.message.unknown4 = "4a2e9bc330dae60e7b74fc85b98868ab4700802e"

    return api_req(api, access_token, req)


def get_api_endpoint(access_token, api = API_URL):
    p_ret = get_profile(access_token, api)
    try:
        return ('https://%s/rpc' % p_ret.api_url)
    except:
        return None


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
    except e:
        if DEBUG:
            print(r1.json()['errors'][0])
        return None

    data1 = {
        'client_id': 'mobile-app_pokemon-go',
        'redirect_uri': 'https://www.nianticlabs.com/pokemongo/error',
        'client_secret': 'w8ScCUXJQc6kXKw8FiOhd8Fixzht18Dq3PEVkUCP5ZPxtgyWsbTvWHFLm2wNY0JR',
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
    parser.add_argument("-d", "--debug", help="Debug Mode", action='store_true')
    parser.set_defaults(DEBUG=True)
    args = parser.parse_args()

    if args.debug:
        global DEBUG
        DEBUG = True
        print('[!] DEBUG mode on')

    set_location(args.location)

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

    response = get_profile(access_token, api_endpoint)
    # response = profile
    # if profile is not None:
    #     print('[+] Login successful')
    #
    #     profile = profile.payload[0].profile
    #     print('[+] Username: {}'.format(profile.username))
    #
    #     creation_time = datetime.fromtimestamp(int(profile.creation_time)/1000)
    #     print('[+] You are playing Pokemon Go since: {}'.format(
    #         creation_time.strftime('%Y-%m-%d %H:%M:%S'),
    #     ))
    #
    #     for curr in profile.currency:
    #         print('[+] {}: {}'.format(curr.type, curr.amount))
    # else:
    #     print('[-] Ooops...')

    # get_second_profile(access_token, api_endpoint, response.unknown7, "\250\251\t\3553\343\320S\305,\226\250>\334\240\032^\211g\221T\3120B\345\026Ia5\312\341\363.\321\234\306\353&\202\355\342\275\021\350\270\f9a\370}\335:\224\330v\355\200\367gl\240\250\004~o\306\017\225\355\026\334?\tXZ(\036\271@\270\360\362z\362\217\376\0054ER\257\360\205\355Q\206\017\2471\251&\231\264\254\n\t\220\"q\304_uxOq\373\n\027\030N\026SG*g\266\241\022\006\302\3034/\266\354Pi\206\252\v\b6\216\256\355\207\360\t\204I\277\373\251\n\243D\226\034\0327\223\340\201\300\245\374\310\235\323\343\301\202J6b\016\220\324\245\246\037\367\256Ku\326\210E\321\246<P\240\324\026\332\373r\311b20\017Z\001\260\243\345t7\343\332\343\212\2308Hx\274\354y\314\300\345$\022\006\255\236\026\217p6o\031\027\273\036\367Z\250T\366\244\254\017\321\a\024<\263\021\370\277\356g\210\033\215\315\v<\241\227\262\210\310-\314>\252N\201\035\362-M\232ghe\205a\270{\304\231\231vWJ\212\226\212\236p\"\243\317\306/?\362\375\370^\351\217\270\373\221\344w\340{_\020\000\274\372\031\377!Cw\025\213\370`+\300\200\000\201\030K\001\206\274m\225%)Z\263\006J\251\212\025\314\315\315\\s\350\367>\333\322e_\337`JGwm\321\\\022\272\372\345\325\264\353G\256\r\t&\220\313\367i\356\354\206V\274\0166g~\324\244\024\377\336\271\235+\025c/_\210\273Z\310MRk\264\233\016w\300r\210\237\253\255v\365\364\201\217\220\025(\357IE\257\247\016\314\016\373\033\036\275Z\210\255\376\376\334f^\272\337\357P\234\025\303\244Ti\024F\321\356\216@L&\353\347\343\225\031\035\360\217\355;i\f\372\234 c\352\000\244\3033=\344WUh<\025\260\375\321\\\234\022\216\006\307\320\213Sv\227f\255\300F\340A,\326r5\370\235\271\330/Q^U\300\333s\377\017d\266\234\347C\003\037D")
    # get_second_profile(access_token, api_endpoint, response.unknown7 , "\337\335cvQ\337R\343Kq\301\300\254\351\363;4\336a:\023\346R\362\vz\023\231D\366\3243@\362\037\315\246\361B\324\250\204Q\361\212X\\W\266\321\341\023(\207?A\330\213\222D\364\241\323v\254|\252H*-f.\022\256A\217!\214\250Y.\271$\336\336\225\035\355\245\317(\31070\271\350D\346\373a`\357L\326>\'D\316d\250\246A\253#A\300\341\001\002\365\r\377\200\005\360|jJcz>Gn\352eL;\320\224\237`\357O\021e\276]\261#\3515\363\273\026\024\246\226\325\325;\t\325!6\330\v\352\276m\n\321\253\266\034X\333%\375v\221\305\016uYF$\313v\304\357?\022\023\256#\277\301\275sM\276\350\342\'\035\030\2342\301\211\275\211\211\376\315\025SKg\376%\331+\351\214^QEf\322~\255\277P\371\253\365L\220\202\b\"Y\253+ \341 )\a\233\245b[\323\234\005{\\e\201Q\307\336e\277O\211\332\211|\227\035\f{\2101\366\240\'\"/\3401\314\330\300\230\324\352\315]Z<\374v\022\373G\353\333<\036\3060\351\256\031\312$\233s\314\32454\271\003Z/\351\242u\000\332w\275\f&C^\270\364iU\361\0047|\023\032lF\207\317\354^\210t+\332S6\207\241^\023n\031\320y\210\376\340\021]x\275^hr`\024!T\344\270\233\333?z\322\a\264\200\026[\322\374*\340-\304.\213\000\a\224\260\022\237\200e\225!aI}\273@\360\272\241\340\005atSn%\345\321\254q\306y\300g\006\301f\277\367R\331q\262\376%\264\243\020P\206\034\002\201\214P\340\005\211\201\320\310\037\332\305\343$\233i\202\352/Vj\375>\241:\3126m\262\323\355\3512tj\371\243\206\0014\256\344w\353\b\327\034\366\003\226\340\324\016n\027\326QUu\375U\2004\237g\244T\345\264\244#\231S\334.\234\217\366%\301\213Hr\362 |\214c\313\253\340c\262$\305\025\263\210")

    m4 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleInt()
    m.f1 = int(time.time() * 1000)
    m4.message = m.SerializeToString()
    m5 = pokemon_pb2.RequestEnvelop.Requests()
    m = pokemon_pb2.RequestEnvelop.MessageSingleString()
    m.bytes = "05daf51635c82611d1aac95c0b051d3ec088a930"
    m5.message = m.SerializeToString()
    #
    # get_second_profile(access_token, api_endpoint, response.unknown7, "LF\030\207\216\330W\004X\372\026\361\211\002\230|\341\207V\213\220\037\227SXC\250\naO\271\264\300Q\nm\017\203\017\212A_K)\373\031\377J.$N\361pKS\234\317PT*\376\030T\255@@\337\377q\305\330\302~\315\357\207\232\003\020\344\353\320/\350T\026\256i\205\313$`\221\370]\241\325\221\311O`\204v$\207vy-\215\203\232bP(\201`\033\362\345\376\203\237\260G.\343*e\351T\250\253\3710/lh9Z\231d\362!\235\a\255\024\004\203\347j\001\335\241\200\3763\220=*L\273\266\022\267\000\212\225\263$\363*\260\376\211\f\235ejX\207\210*\314\251L\212\260[[\302t\356\231x\024\350\020F\346c\341\230\334n\205\025\355\t\276i[\226\356\305<\372Q\000\022\005\224\343\340\230\212S\227\205\0207\217\321Jy\267\354\260BA\241\353\365\240\336\273>.\376\336\021\336C\262\332F\213\202\240\225\277v1\241\370\026V\245\312\261\034&\374\f>\256\263w\204\366\272\203\354=5\203\312\002\250\"\023\331\024:\226\256\017\200k\016\342\373\357\307\266VV\222\231e\372Y*\312\331\336\037,i\002\b\256#\333\317\216\301\243\0164\205x\036\332\236PI_S\320\204\021\320*\363mT\312\231,\343B5\017\024bn\203\320\355\256\355\335<\030\210\\4cZ\216\364\230o\220v\220\373\240\253QzK%\227\333te\344w2\234\216\260%\221\336\nZ\253\330\335\240\310\225.XP\304&\005\034\036r2\2513G+\305\021\004\347\022%\345(\315\361\377\357DF!\203k\030\335J\237\223\212O9\221l\266A\033\a\244\213\001\277\027\232,\274\263\305\b\333N\360\307\327\323\b\2330\020\374}\373\306!MST\265\031o\227\324\023\365)\355\332\273\254\301H\364\'\256P\243\231\021\253\334hr\262\222\321\233CpW\212$m\372>pWl\321/?s\354\354\356\307\363~\303\353\332\241\237;\217\336sZCP\215\267\261",
    #   pokemon_pb2.RequestEnvelop.Requests(), pokemon_pb2.RequestEnvelop.Requests(), m4, pokemon_pb2.RequestEnvelop.Requests(), m5)
    #
    # m1 = pokemon_pb2.RequestEnvelop.Requests()
    # m1.type = 7
    # m = pokemon_pb2.RequestEnvelop.MessageTwoInts()
    # m.f1 = 2
    # m.f5 = 2902
    # m1.message = m.SerializeToString()
    #
    # get_second_profile(access_token, api_endpoint, response.unknown7, "LF\030\207\216\330W\004X\372\026\361\211\002\230|\341\207V\213\220\037\227SXC\250\naO\271\264\231_\276\370\225\3111-aQ)\025\006HQ\370@8$\vi\243\260\241*\375\232\fm\272\016\'n\353\370\204\312f\b\217\301\3129\3577q@\354\205h\372)e\347u\304\254\005\225#\303f\252N\360\021\206\213\245\251q6\024t\274m\375\003\3546Dx\035\236\201\2438A\257\247v\265\367\n\255 \0341d`\v\236h\341P\361\221Q\336\255/;\360y\352\243\334\350>\266\225\f\202\240\350\204\363\373\377>\331.Nm\"&\006\324\352B\362\034\bW)\b\252\256\225\317k\324\r\240\265\377\n\236\2471\371\365]\210s\241\347*\316{\315\371\350\331\305\225\266l\321\243\205\316\321J\001\305\365\244\310\254K=\304\205\260]U\220\214W \017\370\351\304F\340\036\3045n\307\245\351r\320\214w\207\025\203\272\r6\346\306z\346\v\332^\253\033\016\371!\330\f\330\357\0263\275\256ZH\366\360\331\323lX\207c\373m8\207\024\261\0347\366\235\\3\211\345?\315\2348\'\200\317\016\360\253\363\260\320G\002\b\024\303OUV\222\3313\260e\004x\236\356\355\030\237\255v.\252\017\300\377\365\210\363?\264\301\035NpoH\241\274\273\214\v\030sY\300\305\022\034\327\020\240\247\264\355\037\235\314\264g\035\271\2015\256;Eb\026o\304(\202n\256B\204\234\033\267\342z\253\241\376\334\\\261\351\276\000*\210\324\223\025|\347\363$\260\323\214\260\350\255\344\273\305\344\303j\345m\331B\233\320a\265HZ\3049\240GT\2456\245\242l\261\271\236\231P\001\247\356@\263\302\221W\252\366=\342\037\261/\211\265\335`\214\215\017\347\343\306\367\363\221<\222\324~\317\357\375\267\255\034j\t\204%y7tc\234\021\037<\340\372\247\373\021\377\345\210Z\265S\331\v\004\224\221L\3438\232\251Y\017\300\254\245\362\037\200\373}D\347P*\340H\025\262\3449",
    #   m1, pokemon_pb2.RequestEnvelop.Requests(), m4, pokemon_pb2.RequestEnvelop.Requests(), m5)
    #
    # m1 = pokemon_pb2.RequestEnvelop.Requests()
    # m1.type = 300
    # m = pokemon_pb2.RequestEnvelop.MessageTwoInts()
    # m.f1 = 2
    # m.f5 = 2902
    # m1.message = m.SerializeToString()
    #
    # get_second_profile(access_token, api_endpoint, response.unknown7, "\202{s\017\255\325\332\225\337>@\n\370\016\352\234\270\333Q3N<\272\004\250sCo|\253\365\006\027?\220]\231\262R\351\023\277\342\027\260\300\201\262-\310\000\004\322\004\2618\230\357\362\262#B\205\240\274\030\244a\366,\031\265\033\323cdj\351\232W^7\023\021\037=6\263\261\316\304\351\234\3570t\337\340x\234\371\324i\333\374\346>\326\227\336\026\254x\213\001\245\312\210\312X\230&\234\361&)\342\357~\024\226\346$\036@\201.E \326\270H\000\b)\307\351\227\231\213\320\367}wJ\025\316\021$y\364\240\360#r\357\223]kD\273\300\203O\334AD\004\020\005\265DE\\#S};\302-\327\334\350.\032[\203\305\":\227\234n\235\"=XL\004(\023\357u5\3251\341\t\304\037\352\020QOf\267\334\354\340o:N\032\376l\277\222T5/K\314\003\332:\335>\301\335\340`E^\345\321\274B\373\276\221\325\353\210\203J\212\221\373\356\024\314\201\300\351\235 \314\255\243\'\3422\027V\237\331\024\256*z\037^\3634\016-\034\245\3509&\336~u\311a\234\253j\215A`\023%\023\374\270K\020\225\325\b&\317\370\375?z\337\223\017\237e.\016\005\326d\v6i\240\033~%\371\215*\301L\235f\026\023\303\t\357\312\300\254\n%\224\256\251b\202\005\347\267\024\034\235\262<\310\321\362\340\305\024\211Z\245\302\031\270\330\030\312\a|\000\326\r=\324p\336\207\235?a_c\005J6\306Zp\222\306t\036:\253\003&\033\255\372\225\210\271 \374a\371\240\366#\243\341\220>\251\302!\001f\027\202{\257\022=rj\244\205w=\033[Xm\016\314\234\033\215\375\274\376\375\b{\202\266\275\272\206}W\376\224\032\031$\331\265\2123\210\224F0\220\225\332\340\030\224\267\256D+\252\277\320\244\213\220\207*in?zN\340\300D\215\264\212\267\336\"\347\020\301\020\351\303R}\304\340\330\310\342\275\36466\312\304v\314\275",
    #   m1, pokemon_pb2.RequestEnvelop.Requests(), m4, pokemon_pb2.RequestEnvelop.Requests(), m5)


    # m1 = pokemon_pb2.RequestEnvelop.Requests()
    # m1.type = 106
    # m = pokemon_pb2.RequestEnvelop.MessageQuad()
    # wat = pokemon_pb2.RequestEnvelop.Wat()
    # wat.lols.append(384307165696884736)
    # wat.lols.append(384307169991852032)
    # wat.lols.append(1152921499238137856)
    # wat.lols.append(1152921503533105152)
    # wat.lols.append(1152921507828072448)
    # wat.lols.append(1152921512123039744)
    # wat.lols.append(1921535841369325568)
    # wat.lols.append(1921535845664292864)
    # m.f1 = wat.SerializeToString()
    # m.f2 = "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
    # m.lat = COORDS_LATITUDE
    # m.long = COORDS_LONGITUDE
    # m1.message = m.SerializeToString()
    # get_second_profile(access_token, api_endpoint, response.unknown7, "\373\311\337B-\213\216o\347\335\275\f\b\025\257GP\312\335\006\357\222\216~\247\346\017\345\240\"\220?P\016\361\324\305\314\202\003\027U\315y\313\336\2743\265XI\342X\365\213`\331\221\n\204\020\231G9q\235\230\377\316\260\303_B\231\224\024X;8\374\306N8h\270b\274\203z\347\316\332\265\227]7z\314\331\203\351\360\203f\315h\267M\316\006\030\2048\317\261\372m\003C\371\321\372\3732\213\325t\022\274\034\032\235\267\201v\250k\257\363O\217f\261\254UZ\344\223\251Sk\364\vp\225\370S\0259%i\3260at\363\356D\220\034\331\272_q&\367\347\3633q\000^<\215w\324&\2764\305!%\230\323I\351\265\244\215\003dK\230\317\366\313\025\314I\301\322pEj\323\016\213_E\267$n\274\201\226\241\212\312\357*P\227{\220\021nz\367/\037\"\326\337)cL\216\240\305\231v\336\333\275\262\344\351-\231j\205r\r\257N\031;\222\aN\372%\314\216B\3451\227\340q\b\227\316~\023\211\272\255w\037\305\362&&\347\004\217\353\027(\325#;\250\270\327\225/nw\303(\351\232\323v\351(\203\366\"p\201\315g\305\213y\022\201+\f\374\326\266\260[\262\354\233^83\324?\356\205r\354\320\035.d5UEq\2639[\225\213\301}\333g`\021Z\000\232\262@\2069\2266\255\005\210\335\362b\357\a\372\r\335v\364!\357c\302\351R\201\265\304\221\217\037\303nU\t\020\256\262M\233\374\321L\351\224@\350\324K\333f\273}I\334n\234\213f(tB\214\320{\b\361di\254}\223\207\213c\304\245\236G\331wJ\277\264t(!\221\246\344\347\247\026gzZ%\262\202L\205\324\326\314\002\231\336\202\bae\356s\354\357\252$\030\314o\316\377(\3551\310k\275\360\002\303\313hpR\347Lf\343\226\227\234]$Q\213\237\355\372E]Q\345.%\207\347EK\0034_\240\320\000\231\357\320\273\352\004_\244",
    #   m1, pokemon_pb2.RequestEnvelop.Requests(), m4, pokemon_pb2.RequestEnvelop.Requests(), m5)


    walk = sorted(getNeighbors())

    m1 = pokemon_pb2.RequestEnvelop.Requests()
    m1.type = 106
    m = pokemon_pb2.RequestEnvelop.MessageQuad()
    m.f1 = ''.join(map(encode, walk))
    m.f2 = "\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000"
    m.lat = COORDS_LATITUDE
    m.long = COORDS_LONGITUDE
    m1.message = m.SerializeToString()
    get_second_profile(access_token, api_endpoint, response.unknown7, "",
      m1, pokemon_pb2.RequestEnvelop.Requests(), m4, pokemon_pb2.RequestEnvelop.Requests(), m5)


if __name__ == '__main__':
    main()
