
from __future__ import absolute_import

from pgoapi.pgoapi import PGoApi
from pgoapi.rpc_api import RpcApi

# if __name__ != '__main__':
    # try:
        # __import__('pkg_resources').declare_namespace(__name__)
    # except ImportError:
        # __path__ = __import__('pkgutil').extend_path(__path__, __name__)

try:
    import requests.packages.urllib3
    requests.packages.urllib3.disable_warnings()
except:
    pass