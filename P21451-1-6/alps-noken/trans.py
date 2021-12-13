import os
from ftplib import FTP

#ssd_path = 'SmaAgri/Noken/sonoda/sensor1/test.txt'
ssd_path = '/mnt/ssd/sonoda/sensor1/test.txt'

ftp_ssd = FTP('192.168.11.4')
ftp_ssd.set_pasv('true')
ftp_ssd.login('sonoda', 'WestO831')
if os.path.isfile('./test.txt'):
  with open ('./test.txt', 'rb') as f:
    ftp_ssd.storlines('STOR ' + ssd_path, f)
ftp_ssd.close()
