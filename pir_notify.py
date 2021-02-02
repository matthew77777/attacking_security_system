import RPi.GPIO as GPIO
import pygame.mixer
import pygame
import time
import json
import requests
import smtplib, ssl
from email.mime.text import MIMEText
import pigpio

pirPin = 17    #  人感センサを17番ピンに割り当て

# Gmail設定
gmail_account = "tetkifchi7232@gmail.com"
gmail_password = "Tm10280907"

# メール送信先
mail_to = "tetsuya.massuda@gmail.com"

# メールデータ作成
subject = "侵入者検知のお知らせ！！"
body = '侵入者を検知しました。以下のURLにアクセスし部屋の様子を確認してください。 \r\n http://a7c0aab1d0bf.ngrok.io'
msg = MIMEText(body, "html")
msg["Subject"] = subject
msg["To"] = mail_to
msg["From"] = gmail_account

# Gmail接続
server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
    context=ssl.create_default_context())

# HTTPヘッダ設定
HEADERS={ 'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + 'WU1HUeAEEV9DDCOkiSkPf8J+uOTqE6pmJhor0Ck7/3tRF6oA9a38ypCTtgY18pYXQ8Ayi9BTRvZNlN/cYULUCJn9pWXzapNFZcDPZSzNh1OKY88i0ZMO188k/9zc/pPMLnwCy8j3cAIwd2HGJo6TNgdB04t89/1O/w1cDnyilFU=',
}

# POSTデータ設定
POST = {
    'to': 'U577b48525ff52bb66cc9b7dc23946c26',
    'messages': [
        {
            'type': 'text',
            'text': '侵入者を検知しました。http://a7c0aab1d0bf.ngrok.io から部屋の様子を確認してください。'
        }
    ]
}

def setup():
        # GPIOをBCMモードに設定
        GPIO.setmode(GPIO.BCM)
        # pirPinを入力モードに設定
        GPIO.setup(pirPin, GPIO.IN)

def destroy():
        GPIO.cleanup()

def cb(gpio, newLevel, tick):
    firstLoop = True
    while True:
        pir_val = GPIO.input(pirPin)
        if pir_val==GPIO.HIGH:
            if firstLoop:	
                #LINEメッセージ送信
                CH = 'https://api.line.me/v2/bot/message/push'
                REQ = requests.post(CH, headers=HEADERS, data=json.dumps(POST))

                #正常であればHTTPステータス200を表示
                print(REQ.status_code)
                if REQ.status_code != 200:
                    print(REQ.text)

                #Gmail送信
                server.login(gmail_account, gmail_password)
                server.send_message(msg)
                print("ok.")
                firstLoop = False
  	
pi = pigpio.pi()
pi.set_mode(pirPin, pigpio.INPUT)
cb = pi.callback(pirPin,pigpio.RISING_EDGE,cb)
pi.set_pull_up_down(pirPin, pigpio.PUD_UP)

if __name__ == '__main__': 
    setup()
    try: 
       while(True):
           time.sleep(1) 

    except KeyboardInterrupt:
        destroy()
