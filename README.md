[![Build Status](https://travis-ci.org/tejado/pgoapi.svg?branch=master)](https://travis-ci.org/tejado/pgoapi)




# pgoapi - a python pokemon go api lib/demo
pgoapi is a client/api/demo for Pokemon Go by https://github.com/tejado.  
It allows automatic parsing of requests/responses by finding the correct protobuf objects over a naming convention and will return the response in a parsed python dictionary format.   

 * This is unofficial - USE AT YOUR OWN RISK !
 * I don't play pokemon go !
 * No bot/farming code included !

## Supports
 * Python 2 and 3
 * Google/PTC auth
 * Address parsing for GPS coordinates
 * Allows chaining of RPC calls
 * Good logging/debugging possibilities
 * Easy extension of further calls! No source code change required!
 * Uses [POGOProtos](https://github.com/AeonLucid/POGOProtos)
 * Following RPC calls:
   * GET_PLAYER
   * GET_INVENTORY
   * GET_MAP_OBJECTS
   * DOWNLOAD_SETTINGS
   * DOWNLOAD_ITEM_TEMPLATES
   * CHECK_AWARDED_BADGES
   * FORT_SEARCH (spinning of pokestops)
   * RELEASE_POKEMON (release pokemon and get candy/xp)
   * EVOLVE_POKEMON
   * ...
   * more should be possible now but have to be tested (PLEASE support here)

## Installation (lib only - without pokecli etc.)

    pip.exe install  git+https://github.com/tejado/pgoapi.git

## Usage

### pokecli
    usage: pokecli.py [-h] -a AUTH_SERVICE -u USERNAME -p PASSWORD -l LOCATION [-d] [-t]

    optional arguments:
      -h, --help                                    show this help message and exit
      -a AUTH_SERVICE, --auth_service AUTH_SERVICE  Auth Service ('ptc' or 'google')
      -u USERNAME, --username USERNAME              Username
      -p PASSWORD, --password PASSWORD              Password
      -l LOCATION, --location LOCATION              Location
      -d, --debug                                   Debug Mode
      -t, --test                                    Only parse the specified location

### pokecli demo

    $ python2 pokecli.py -a ptc -u tejado -p 1234 --location "New York, Washington Square"
    2016-07-19 01:22:14,806 [   pokecli] [ INFO] Your given location: Washington Square, Greenwich, NY 12834, USA
    2016-07-19 01:22:14,806 [   pokecli] [ INFO] lat/long/alt: 43.0909305 -73.4989367 0.0
    2016-07-19 01:22:14,808 [  auth_ptc] [ INFO] Login for: tejado
    2016-07-19 01:22:15,584 [  auth_ptc] [ INFO] PTC Login successful
    2016-07-19 01:22:15,584 [    pgoapi] [ INFO] Starting RPC login sequence (app simulation)
    2016-07-19 01:22:15,584 [    pgoapi] [ INFO] Create new request...
    2016-07-19 01:22:15,584 [    pgoapi] [ INFO] Adding 'GET_PLAYER' to RPC request
    2016-07-19 01:22:15,584 [    pgoapi] [ INFO] Adding 'GET_HATCHED_EGGS' to RPC request
    2016-07-19 01:22:15,584 [    pgoapi] [ INFO] Adding 'GET_INVENTORY' to RPC request
    2016-07-19 01:22:15,584 [    pgoapi] [ INFO] Adding 'CHECK_AWARDED_BADGES' to RPC request
    2016-07-19 01:22:15,584 [    pgoapi] [ INFO] Adding 'DOWNLOAD_SETTINGS' to RPC request including arguments
    2016-07-19 01:22:15,585 [    pgoapi] [ INFO] Execution of RPC
    2016-07-19 01:22:16,259 [    pgoapi] [ INFO] Cleanup of request!
    2016-07-19 01:22:16,259 [    pgoapi] [ INFO] Finished RPC login sequence (app simulation)
    2016-07-19 01:22:16,259 [    pgoapi] [ INFO] Login process completed
    2016-07-19 01:22:16,259 [    pgoapi] [ INFO] Create new request...
    2016-07-19 01:22:16,259 [    pgoapi] [ INFO] Adding 'GET_PLAYER' to RPC request
    2016-07-19 01:22:16,259 [    pgoapi] [ INFO] Execution of RPC
    2016-07-19 01:22:16,907 [    pgoapi] [ INFO] Cleanup of request!
    Response dictionary:
    ...
          "profile": {
            "username": "tejado",
            "item_storage": 350,
            "unknown12": "",
            "unknown13": "",
            "creation_time": 1468139...,
            "currency": [
              {
                "type": "POKECOIN"
              },
              {
                "amount": 400,
                "type": "STARDUST"
              }
            ],
            "daily_bonus": {},
            "avatar": {
              "unknown2": 1,
              "unknown3": 4,
              "unknown9": 2,
              "unknown10": 1
            },
            "tutorial": "AAEDBAc=\n",
            "poke_storage": 250
          },
    ...


### pokecli with Docker (optional)
Build and run container:

    docker build -t pokecli .
    docker run pokecli

Optionally create an alias:

    alias pokecli='docker run pokecli'

## pgoapi extension
All (known) RPC calls against the original Pokemon Go servers are listed in the RequestType Enum in the [POGOProtos/Networking/Requests/RequestType.proto](https://github.com/AeonLucid/POGOProtos/blob/master/src/POGOProtos/Networking/Requests/RequestType.proto) file. These can be executed over the name, e.g. the call for get_player is:

    api = PGoApi()
    ...
    api.get_player()
    api.call()

The pgoapi will send this as a RPC request and tries to parse the response over a protobuf object with the same name (get_player) converted to CamelCase + 'Response'. In our example, it would be 'GetPlayerResponse'.

If a request needs parameters, they can be added as arguments and pgoapi will try to add them automatically to the request, e.g.:

    *DownloadSettingsMessage.proto:*
    message DownloadSettingsMessage {
      optional string hash = 1;
    }

    *python:*
    api = PGoApi()
    ...
    api.download_settings(hash="4a2e9bc330dae60e7b74fc85b98868ab4700802e")
    api.call()

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
Setup by [mikeres0](https://github.com/mikeres0)
Auto signup [repo](https://github.com/mikeres0/PgoAPI-Slack-Signup)

## Credits
[Mila432](https://github.com/Mila432/Pokemon_Go_API) for the login secrets  
[elliottcarlson](https://github.com/elliottcarlson) for the Google Auth PR  
[AeonLucid](https://github.com/AeonLucid/POGOProtos) for improved protos  
[AHAAAAAAA](https://github.com/AHAAAAAAA/PokemonGo-Map) for parts of the s2sphere stuff

## Ports
[C# Port](https://github.com/BclEx/pokemongo-api-demo.net) by BclEx  
[Node Port](https://github.com/Armax/Pokemon-GO-node-api) by Arm4x  
