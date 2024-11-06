# SecureRoom
SecureRoom is a project I have made for my third year school project.
It is a an online conference room reservation system using a NFC reader and a Nuki Smart Lock gen 4 

# How to deploy
First, clone the git

Then go inside installation folder, there you'll find 4 scripts

installPackages, that will install all dependancies

installFiles, that will put every files inside the good folder

configMqtt, that will disable anonymous login and add a user to the MQTT broker mosquitto

installBackup, that will erase sdb1 disk, reformat it, create folders and create a crontab to move db inside of the second disk

By simply executing each of these in order, you'll get the webapp on your server IP

If you cant execute a script, you need to install dos2unix : sudo apt install dos2unix
then execute it on each files : sudo dos2unix SecureRoom/installation/*


# Other
The code comments are in french as it is my main language

Nezuloxx // 
