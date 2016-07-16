# Pokemon Go API Demo

 * USE AT YOUR OWN RISK !
 * includes protobuf file
 * maybe you should change some of the proto values like gps cords...
 * ugly code

## Demo

    $ python main.py -u *** -p *** --location "Union Square, San Francisco"
    [!] Your given location: Union Square, San Francisco, CA 94108, USA
    [!] lat/long/alt: 37.7879938 -122.4074374 0.0
    [!] login for: ***
    [+] RPC Session Token: TGT-***-****** ...
    [+] Received API endpoint: https://pgorelease.nianticlabs.com/plfe/208/rpc
    [+] Login successful
    [+] Username: Mehbasaur
    [+] You are playing Pokemon Go since: 2016-07-14 22:48:54
    [+] POKECOIN: 0
    [+] STARDUST: 100

    Within one step of LatLng: 37.7861784887,-122.408499387 (222m SW from you):
        (92) Gastly
    Within one step of LatLng: 37.7885606156,-122.408499387 (112m NW from you):
        (21) Spearow
        (41) Zubat
        (32) Nidoran ♂

    (21) Spearow is visible at (37.7886329623, -122.407658647) for 169 seconds (73m NW from you)
    (41) Zubat is visible at (37.7887988683, -122.409782609) for 70 seconds (224m NW from you)
    (32) Nidoran ♂ is visible at (37.7885226453, -122.408986128) for 805 seconds (148m NW from you)
    (41) Zubat is visible at (37.7890195112, -122.40712765) for 84 seconds (117m NE from you)
    (23) Ekans is visible at (37.7900544956, -122.407393149) for 227 seconds (229m N from you)
    (92) Gastly is visible at (37.7869393568, -122.408809132) for 356 seconds (168m SW from you)

## Credits
Thanks a lot to [Mila432](https://github.com/Mila432/Pokemon_Go_API) !
