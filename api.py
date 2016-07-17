import requests
import pokemon_pb2
import settings
from location import get_location_coords
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

API_URL = 'https://pgorelease.nianticlabs.com/plfe/rpc'

SESSION = requests.session()
SESSION.headers.update({'User-Agent': 'Niantic App'})
SESSION.verify = False

def api_req(service, api_endpoint, access_token, req):
    try:
        p_req = pokemon_pb2.RequestEnvelop()
        p_req.unknown1 = 2
        p_req.rpc_id = 8145806132888207460

        p_req.requests.MergeFrom(req)

        p_req.latitude, p_req.longitude, p_req.altitude = get_location_coords()

        p_req.unknown12 = 989
        p_req.auth.provider = service
        p_req.auth.token.contents = access_token
        p_req.auth.token.unknown13 = 59
        protobuf = p_req.SerializeToString()

        r = SESSION.post(api_endpoint, data=protobuf, verify=False)

        p_ret = pokemon_pb2.ResponseEnvelop()
        p_ret.ParseFromString(r.content)
        return p_ret
    except Exception,e:
        if settings.debug:
            print(e)
        return None


def get_api_endpoint(service, access_token):
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

    p_ret = api_req(service, API_URL, access_token, req.requests)

    try:
        return ('https://%s/rpc' % p_ret.api_url)
    except:
        return None