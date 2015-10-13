# domogik-plugin-k8056
Domogik Plugin for k8056 board



## Plugin purpose

### K8056 relay board management 

Command on,off and pulse relay of K8056 board With xPL Messages

    Technical Description of K8056 Board serial protocol

    Port RS232 is configure with this setting: 2400/8/n/1
    To control the k8056 card, the correct sequence needs to be send like this:
        Ascii code 13
        Card address (1..255)
        Instruction (see below), only supported now 'S'|'C'|'T' set/clear/toggle
        Relay #('1'..'9'), 9 for all relay. 
        Checkum, it is the 2-complement of the sum of the 4 previous bytes + 1. 
            In Python, checksum = ( 255 - (13 + int('1') + ord('S') + ord('1')) % 256 ) + 1

    Instructions:
        'E': Emergency stop all cards.
        'D': Display address of all cards in a binary fashion (LD1:MSB, LD8:LSB)
        'S': Set a relay, followed by relay # ('1'..'9' in ASCII), 9 for all relay.
        'C': Clear a relay, followed by relay # ('1'..'9' in ASCII), 9 for all relay.
        'T': Toggle a relay, followed by relay # ('1'..'8' in ASCII).
        'A': Change the current address of a card, followed by the address (1..255)
        'F': Force all cards address to 1 (default)
        'B': Send a byte, Allows to control the 8 relays in 1 byte (LD1:MSB, LD8:LSB) 


### Listeners
Message example: xpl-cmnd control.basic { device=k8056-1 type=R1  current=high }

(Relais #1 of K8056 board #1)

### ACK xpl-stat message to respond for xpl-cmnd command
xpl-stat sensor.basic  device=k8056-1 type=R1 current=high

