
from __future__ import absolute_import

from pgoapi.pgoapi import PGoApi
from pgoapi.rpc_api import RpcApi
from pgoapi.auth import Auth

try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
except:
    pass