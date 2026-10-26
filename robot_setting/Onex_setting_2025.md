## Basic Setup

1) install ubuntu
2) git ssh
3) install raisim, raisin
4) 

## Robot ssh
`touch ~/.ssh/config`

Write:

```
Host robot
    HostName 192.168.12.1
    User root

Host raiway
    HostName 192.168.12.1
    User raiway
```
## gui.sh
To ~/Desktop/gui.sh

```
#!/bin/bash

cd /home/raiway/raisin_ws
source /home/raiway/raisin_ws/install/setup.bash
ros2 run raisin_gui raisin_gui
```