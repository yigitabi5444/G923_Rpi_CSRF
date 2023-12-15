#Add lg4ff to kernel
pip install pygame
sudo apt-get install dkms
cd /usr/src
sudo git clone https://github.com/berarma/new-lg4ff.git
sudo dkms install /usr/src/new-lg4ff
# Add sudo update-initramfs -u  to /etc/rc.local
sudo sed -i -e '$i \sudo update-initramfs -u\n' /etc/rc.local
sudo reboot
