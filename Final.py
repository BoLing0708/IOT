import time,mfrc522,network, urequests
from machine import Pin,time_pulse_us,PWM
rfid=mfrc522.MFRC522(0,2,4,5,14)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("ASUS_18_2G", "nptu404ab")
def ping(trigPin, echoPin):
    trig=Pin(trigPin, Pin.OUT)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    ret=time_pulse_us(Pin(echoPin),1)
    if ret == -2: #no pulse
        duration=0
    elif ret == -1: #pulse no ending
        duration=1000000
    else:
        duration=ret
    return duration

temperature=25
velocity=331.5 + 0.6*temperature
#led=Pin(15,Pin.OUT)
def alarmBeep(pwm):
    #當被呼叫時，立即發送line訊息提醒
    urequests.get("http://maker.ifttt.com/trigger/BeefNoodles/with/key/bptNB3o0-7DqUh6j_poA_M")
    print("send")
    #當被呼叫時，持續做蜂鳴器發聲
    while True:
        #當被呼叫時，代表sensor已偵測有破壞、壞人靠近，因此我們先檢測是否誤觸或是屋主回來
        rfid=mfrc522.MFRC522(0,2,4,5,14)        
        stat,tag_type=rfid.request(rfid.REQIDL)
        if stat==rfid.OK:
            stat,raw_uid=rfid.anticoll()
        if stat==rfid.OK: #如果有偵測到RFID卡片的讀取則
            id="%02x%02x%02x%02x"%(raw_uid[0],raw_uid[1],raw_uid[2],raw_uid[3]) 
            print("卡號:",id) #印出解除警報之卡片
            time.sleep(0.1)
            pwm.deinit()
            break #表警報解除 因此跳出while迴圈，結束蜂鳴器呼叫聲
        pwm.freq(1000)     #由此可控制蜂鳴器大小聲
        pwm.duty(128)
    
    
      

pwm=PWM(Pin(12))
shock=Pin(16,Pin.IN)

while True:
    duration=ping(trigPin=13,echoPin=15)/1000000/2   #unit=second, single way
    distance=round(duration*velocity*100) 
    print(shock.value())
    print('%scm' % distance)
    #假如震動感測模組偵測到晃動(即狀態回傳為1)
    #或是超音波感測距離器偵測到有物體靠近，並且距離<=5
    #則呼叫蜂鳴器警報發聲模組加以警示
    if shock.value()==1 or distance<=5: 
        alarmBeep(pwm)
    #若沒有則蜂鳴器停止運作
    else:
        pwm.deinit()
    time.sleep(1)
    pwm.deinit()