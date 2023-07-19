rem gets crypad.dat from bku1 for crypad

scp pi@%BKUIP%:/mnt/data/urls.txt urls.txx
echo "converting urls.txx to urls.txt ..."
python fixurls.py
