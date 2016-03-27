#!/usr/bin/env python
# -*- coding: utf-8 -*-

#####################################################################################各種インポート
import pygame
from pygame.locals import *
import sys
import time
from time import sleep
from datetime import datetime
from notsmb import notSMB
import csv
import locale
import serial
from struct import *
from xbee import XBee,ZigBee

#####################################################################################各種関数宣言
def splitStr2(str, num):
    l = []
    for i in range(num):
        l.append(str[i::num])
    l = ["".join(i) for i in zip(*l)]
    rem = len(str) % num  
    if rem:
        l.append(str[-rem:])
    return l

def GET_CO2():
	
	co2_data_raw =[0,0,0,0]
	co2_data =[0,0,0,0]
	co2_trash =[0,0,0,0]
	last_co2_value = 0
	co2_value =0
	
	while True:
		try:
			co2_data_raw = bus.i2c(CO2_ADDR,[0x22,0x00,0x08,0x2A],4)
			
		except: 
			blank1 =0
		
		if not(co2_data_raw[0]==33):
			co2_trash = co2_data_raw
			continue
			
		else:
			co2_data = co2_data_raw
			co2_value = (co2_data[1]*256) + co2_data[2]
			break
		
	last_co2_value =  co2_value
	return 	co2_value
		
def GET_COMPASS():

	compass_data =[0,0]
	compass_value =0
	
	while True:
		try:
			compass_data = bus.i2c(COMPASS_ADDR,[0x47,0x74,0x72],2)
			compass_value = (compass_data[0]*256) + compass_data[1]
			break
		except:
			blank2 =0
	
	return 	compass_value	

def GET_TEMPERATURE():

	temperature_data =[0,0,0]
	temperature_value =0
	temperature_temp = 0
	last_temperature_temp = 0
	
	while True:
		blank = 1;
	
		try:
			bus.i2c(SHT25_ADDR,[0xf3],0)
		except:
			blank =0;

		if blank != 0:
			temperature_data = 1
			while temperature_data < 200:
				try:
					temperature_data = bus.i2c(SHT25_ADDR,[],3)
				except:
					temperature_data+=1
					time.sleep(0.01)

		if blank == 0:
			continue
		elif temperature_data == 200:
			temperature_temp = last_temperature_temp
			break
		else:
			temperature_value = (temperature_data[0]*256) + temperature_data[1]
			temperature_temp = -46.85 + (175.72/65536.0)*temperature_value
			break
	
	if temperature_temp > 100:
		temperature_temp =  last_temperature_temp
	elif temperature_temp == 0:
		temperature_temp =  last_temperature_temp
	last_temperature_temp =  temperature_temp
	return 	temperature_temp
	
def GET_HUMIDITY():

	humidity_data =[0,0,0]
	humidity_value =0
	humidity_temp = 0
	last_humidity_temp = 0
	error_humidity = 0
	
	while True:
		blank = 1;
		try:
			bus.i2c(SHT25_ADDR,[0xf5],0)
		except:
			blank =0;

		if blank != 0:
			humidity_data = 1
			while humidity_data < 256:
				try:
					humidity_data = bus.i2c(SHT25_ADDR,[],3)
				except:
					humidity_data+=1
					time.sleep(0.01)
			
		if blank == 0:
			continue
		elif humidity_data == 256:
			humidity_temp = last_humidity_temp
		else:
			humidity_value = (humidity_data[0]*256) + humidity_data[1]
			humidity_temp = -6.0 + (125.0 / 65536.0)*humidity_value
			break
	
	if humidity_temp > 100:
		humidity_temp =  last_humidity_temp
	elif humidity_temp == 0:
		humidity_temp =  last_humidity_temp

	last_humidity_temp =  humidity_temp
	return humidity_temp

####################################################################################シリアル関連
ser = serial.Serial('/dev/ttyUSB2', 57600)
print ser
xbee = ZigBee(ser,escaped=True)

#####################################################################################ファイル関係

f1 = open('co2.csv', 'ab')
f2 = open('compass.csv', 'ab')
f3 = open('temperature.csv', 'ab')
f4 = open('humidity.csv', 'ab')

print"I2CSTART"

#####################################################################################pygame関係

SCREEN_SIZE = (200, 200)
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("キーイベント2")

#####################################################################################I2C関係
COMPASS_ADDR = 0x21
SHT25_ADDR = 0x40
CO2_ADDR = 0x68
I2CBUS = 1
bus = notSMB(I2CBUS)

#####################################################################################CO2関係
co2 = 0

#####################################################################################コンパス関係
compass = 0

#####################################################################################温度関係
temperature = 0

#####################################################################################湿度関係
humidity = 0

#####################################################################################時間関係
starttime = 0
nowtime = 0
lasttime = 0
dt = 0
result = 0
last_result = 0

#####################################################################################XBee関係
COORDINATOR_ADRR = "\x00\x13\xA2\x00\x40\x99\xD8\x9F"

if __name__ == "__main__":

	starttime = datetime.now()

	print(starttime)
	while True:
	
#####################################################################################センサの値取得	
		co2 = GET_CO2()
		compass = GET_COMPASS()
		temperature = GET_TEMPERATURE()
		humidity = GET_HUMIDITY()
		
		temperature2 = temperature*100
		humidity2 = humidity*100
		
		print"co2"
		print(co2)
		print"compass"
		print(compass)
		print"temperature"
		print(temperature2)
		print"humidity"
		print(humidity2)
	
#####################################################################################送信データ生成
		data = []
		data.append(pack('H',co2))
		data.append(pack('H',compass))
		data.append(pack('H',temperature2))
		data.append(pack('H',humidity2))
		data = "".join(map(str,data))
		
		print pack('H',co2).encode("hex_codec")
		print pack('H',compass).encode("hex_codec")
		print pack('H',temperature2).encode("hex_codec")
		print pack('H',humidity2).encode("hex_codec")
		print data.encode("hex_codec")
				
#####################################################################################時間記録
		nowtime = 0
		dt = 0
		result = 0
		nowtime = datetime.now()
		dt = nowtime-starttime
		result = dt.seconds + float(dt.microseconds)/1000000

#####################################################################################データ保存
		buffer_co2 = [result,co2]
		buffer_compass = [result,compass]
		buffer_temperature = [result,temperature]
		buffer_humidity = [result,humidity]
		
		csvWriter = csv.writer(f1)
		csvWriter.writerow(buffer_co2)
		csvWriter = csv.writer(f2)
		csvWriter.writerow(buffer_compass)
		csvWriter = csv.writer(f3)
		csvWriter.writerow(buffer_temperature)
		csvWriter = csv.writer(f4)
		csvWriter.writerow(buffer_humidity)

#####################################################################################データ送信
		xbee.tx(dest_addr_long=COORDINATOR_ADRR,dest_addr = "\xFF\xFE",data=data)

		pressed_keys = pygame.key.get_pressed()
		for event in pygame.event.get():
			if event.type == QUIT: 
				sys.exit()
			if event.type == KEYDOWN:  # キーを押したとき
				# ESCキーならスクリプトを終了
				if event.key == K_ESCAPE:
					sys.exit()
					
