#!/usr/bin/python3
from bluepy import btle
from omron_env_broadcast import ScanDelegate

#omron_env_broadcast.pyのセンサ値取得デリゲートを、スキャン時実行に設定
scanner = btle.Scanner().withDelegate(ScanDelegate())
#スキャンしてセンサ値取得（タイムアウト5秒）
scanner.scan(5.0)
#試しに温度を表示
print("SensorType", scanner.delegate.sensorValue['SensorType'])
print("Temperature", scanner.delegate.sensorValue['Temperature'])
print("Humidity", scanner.delegate.sensorValue['Humidity'])
print("Brightness", scanner.delegate.sensorValue['Light'])
print("UV", scanner.delegate.sensorValue['UV'])
print("Pressure", scanner.delegate.sensorValue['Pressure'])
print("Noise", scanner.delegate.sensorValue['Noise'])
print("Discomfort", scanner.delegate.sensorValue['Discomfort'])
print("WBGT", scanner.delegate.sensorValue['WBGT'])
print("BatteryVoltage", scanner.delegate.sensorValue['BatteryVoltage'])
