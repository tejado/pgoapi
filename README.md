[![Build Status](https://travis-ci.org/tejado/pgoapi.svg?branch=master)](https://travis-ci.org/tejado/pgoapi)

# pgoapi - a pokemon go api lib in python
pgoapi is a client/api/demo for Pokemon Go by https://github.com/tejado.  
It allows automatic parsing of requests/responses by finding the correct protobuf objects over a naming convention and will return the response in a parsed python dictionary format.   

 * This is unofficial - USE AT YOUR OWN RISK !
 * I don't play pokemon go !
 * No bot/farming code included !

## Feature Support
 * Python 2 and 3
 * Google/PTC auth
 * Address parsing for GPS coordinates
 * Allows chaining of RPC calls
 * Re-auth if ticket expired
 * Check for server side-throttling
 * Thread-safety
 * Advanced logging/debugging
 * Uses [POGOProtos](https://github.com/AeonLucid/POGOProtos)
 * Mostly all available RPC calls (see [API reference](https://github.com/tejado/pgoapi/wiki/api_functions) on the wiki)

## Documentation
Documentation is available at the github [pgoapi wiki](https://github.com/tejado/pgoapi/wiki).

## Requirements
 * Python 2 or 3
 * requests
 * protobuf (>=3)
 * gpsoauth
 * geopy (only for pokecli demo)
 * s2sphere (only for pokecli demo)

## Contribution
Contributions are highly welcome. Please use github or [pgoapi.slack.com](https://pgoapi.slack.com) for it!  
Join pgoapi.slack.com [here](https://pgoapislack.herokuapp.com/)!

## Credits
[Mila432](https://github.com/Mila432/Pokemon_Go_API) for the login secrets  
[elliottcarlson](https://github.com/elliottcarlson) for the Google Auth PR  
[AeonLucid](https://github.com/AeonLucid/POGOProtos) for improved protos  
[AHAAAAAAA](https://github.com/AHAAAAAAA/PokemonGo-Map) for parts of the s2sphere stuff  
[mikeres0](https://github.com/mikeres0) for the slack channel including auto signup  
[DeirhX](https://github.com/DeirhX) for thread-safety

## Ports
[Node Port](https://github.com/Armax/Pokemon-GO-node-api) by Arm4x  
[Node Port - pogobuf](https://github.com/cyraxx/pogobuf) by cyraxx 

[![Analytics](https://ga-beacon.appspot.com/UA-1911411-4/pgoapi.git/README.md?pixel&useReferer)](https://github.com/igrigorik/ga-beacon)
