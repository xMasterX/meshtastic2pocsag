# meshtastic2pocsag
Python bridge from wifi connected node to rpitx pocsag app that transmits pocsag messages to the air
 <br> <br>
Use raspberry pi,  <br>
setup python 3.13.9 with `pyenv` while being in user shell <br>
do `pip install meshtastic pubsub` <br>
download/compile and place rpitx at this path `/home/pi/rpitx` <br>
edit `m2p.py` enter your friendly nodes id's that are starting with `!` <br>
enter your pocsag capcodes for getting direct messages - with sound <br>
and mail capcode for all other messages (in channels) <br>
edit frequency <br>
edit your node IP address at the end <br>
 <br>
Run `python m2p.py` and send message to your node - rpi should retransmit it via pocsag to selected capcode!
