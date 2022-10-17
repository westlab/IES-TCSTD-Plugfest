## omron_envsensor - オムロン環境センサ受信スクリプトライブラリ

### 取り扱い方

omron_envsensorは、RaspberryPi上のLinuxシステム上からpythonスクリプトからインポートもしくはrun.py、cat_csv.pyファイルを用いて活性化してください。
活性化する際にはroot権限と、必須パッケージがインストールされていなければいけません。
必須パッケージのインストールについては **補遺1** を参照してください。
ライブラリのインストールについては **補遺2** を参照してください。


### 概要

omron_envsensorは、およそ6つのファイルからなるpython言語で書かれた[オムロン環境センサ](http://www.omron.co.jp/ecb/product-info/sensor/iot-sensor/environmental-sensor)受信スクリプトです。
活性化されると機器のBluetooth機能よりパケットを傍受し、特定の機器のパケットをパースして返します。

omron_envsensorの活性化には特定のパッケージがインストールされていないと、通常のpython言語のエラーメッセージと共に動作を停止します。
使用するpythonは2,3どちらでも構いません。

このライブラリは[OmronMicroDevices/envsensor-observer-py](https://github.com/OmronMicroDevices/envsensor-observer-py)を参考に作られています。


### 補遺1 必須パッケージのインストール

``` shell
sudo apt-get install -y libperl-dev
sudo apt-get install -y libgtk2.0-dev
sudo apt-get install -y libglib2.0
sudo apt-get install -y libbluetooth-dev libreadline-dev
sudo apt-get install -y libboost-python-dev libboost-thread-dev libboost-python-dev

sudo pip3 install pybluez
sudo pip3 install pygattlib
```


### 補遺2 インストール

```shell
sudo pip3 install https://github.com/isaaxug/omron_envsensor/archive/0.0.3.zip
```

### 補遺3 サンプルスクリプトの使用方法

info情報
```shell
sudo python3 run.py
```

CSV出力
```shell
sudo python3 cat_csv.py > csv.csv
```

