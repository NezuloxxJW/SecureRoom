sudo apt update
sudo apt install -y python3 python3-pip mosquitto sqlite3 nginx --fix-missing
pip -version

sudo pip install bcrypt nfcpy paho-mqtt waitress flask flask_cors flask_limiter --break-system-packages
