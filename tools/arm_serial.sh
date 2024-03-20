ws_path=$(pwd)
echo $ws_path

cd $ws_path/camera_ws

file="/etc/udev/rules.d/arx_can.rules"

if [[ -f "$file" ]]; then
    echo "arx_can.rules exist."
else
    echo
    echo "arx_can.rules no exist, please add arx_can.rules."
    echo
    exit 0
fi


echo "ls /dev/ttyACM*"
echo
echo "udevadm info -a -n /dev/ttyACM* | grep serial"
echo
echo "sudo vim /etc/udev/rules.d/arx_can.rules"

echo "ssh-keygen -f "/home/lin/.ssh/known_hosts" -R "192.168.1.121""