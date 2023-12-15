#Add lg4ff to kernel
sudo pip install --upgrade pip
sudo pip install crsf-parser
sudo pip install pygame
sudo pip install --upgrade pygame
sudo apt-get install dkms
cd /usr/src
sudo git clone https://github.com/berarma/new-lg4ff.git
sudo dkms install /usr/src/new-lg4ff
# Add sudo update-initramfs -u  to /etc/rc.local
sudo sed -i -e '$i \sudo update-initramfs -u\n' /etc/rc.local
# Add enable_uart=1 to /boot/config.txt
sudo sed -i -e '$i \enable_uart=1\n' /boot/config.txt
# remove console=serial0,115200 from /boot/cmdline.txt
sudo sed -i -e 's/console=serial0,115200 //g' /boot/cmdline.txt
sudo reboot
