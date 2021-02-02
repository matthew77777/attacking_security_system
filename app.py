import sys
sys.path.append('/home/pi/.local/lib/python3.7/site-packages/cv2')
sys.path.append('/home/pi/.local/lib/python3.7/site-packages/flask_login')
import sqlite3
import cv2
from flask import Flask, redirect, render_template, request, Response, url_for, abort
from camera import Camera
import RPi.GPIO as GPIO
import signal
import pigpio
import time
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict
import pygame.mixer
import pygame
from time import sleep
import subprocess

app = Flask(__name__)

motorPin = (18,23,24,25)
rolePerMinute =15
BeepPin = 16
stepsPerRevolution = 2048
stepSpeed = (600/rolePerMinute)/stepsPerRevolution

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for i in motorPin:
        GPIO.setup(i, GPIO.OUT)

login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secret"

class User(UserMixin):
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password
dbname = 'USERINFO.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()
list = []
for user in cur.execute("select * from user"):
    list.append(user[0])
    list.append(user[1])
    list.append(user[2])

users = {
    1: User(list[0], list[1], list[2]),
    2: User(list[3], list[4], list[5])
}

nested_dict = lambda: defaultdict(nested_dict)
user_check = nested_dict()
for i in users.values():
    user_check[i.name]["password"] = i.password
    user_check[i.name]["id"] = i.id


@login_manager.user_loader
def load_user(user_id):
    return users.get(int(user_id))

@app.route("/")
def index():
    return redirect(url_for('login'))

@login_required
@app.route('/login/', methods=["GET", "POST"])
def login():
    if(request.method == "POST"):
        # ユーザーチェック
        if(request.form["username"] in user_check and request.form["password"] == user_check[request.form["username"]]["password"]):
            # ユーザーが存在した場合はログイン
            login_user(users.get(user_check[request.form["username"]]["id"]))
            return render_template("stream.html")
        else:
            return abort(401)
    else:
        return render_template("login.html")

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/stream")
@login_required
def stream():
    return render_template("stream.html")

@app.route("/system_start/")
@login_required
def system_start():
    command = ["python", "system_start.py"]
    proc = subprocess.Popen(command) 
    print("システムを起動しました")
    return render_template("stream.html")

@app.route("/system_stop/")
@login_required
def system_stop():
    subprocess.run(["./system_stop.sh"])
    print("システムを停止しました")
    return render_template("stream.html")

def gen(camera):
    while True:
        frame = camera.get_frame()

        if frame is not None:
            yield (b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame.tobytes() + b"\r\n")
        else:
            print("frame is none")

@app.route("/video_feed")
def video_feed():
    return Response(gen(Camera()),
            mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route('/forward')
def forward():
    left_out = 26
    pi.set_mode(left_out, pigpio.OUTPUT)
    pi.set_servo_pulsewidth(left_out, 1000) 
    time.sleep(1)
    pi.set_servo_pulsewidth(left_out, 2500)
    time.sleep(1)
    #pi.set_servo_pulsewidth(left_out, 1000)
    #time.sleep(1)
    pi.set_mode(left_out, pigpio.INPUT)
    return redirect(url_for('stream'))

@app.route('/right')
def right():
    pi.set_servo_pulsewidth(left_out, 2500)
    time.sleep(1)
    pi.set_servo_pulsewidth(left_out, 500)
    return redirect(url_for('stream'))

@app.route('/speaker')
def speaker():
    pygame.mixer.init()
    pygame.mixer.music.load("warning.mp3")
    pygame.mixer.music.play(-1)
    time.sleep(12)
    pygame.mixer.music.stop() 
    return redirect(url_for('stream'))

@app.route('/led_on')
def led_on():
    subprocess.call('./led_on')
    return redirect(url_for('stream'))

@app.route('/led_off')
def led_off():
    subprocess.call('./led_off')
    return redirect(url_for('stream'))

@app.route('/gas_on')
def gas_on():
    subprocess.call('./gas_on')
    return redirect(url_for('stream'))

@app.route('/gas_off')
def gas_off():
    subprocess.call('./gas_off')
    return redirect(url_for('stream'))

@app.route('/clock')
def clock():
    for j in range(12):
        for i in range(4):
            GPIO.output(motorPin[i],0x99>>j & (0x08>>i))
        sleep(stepSpeed)
    return redirect(url_for('stream'))

@app.route('/anticlock')
def anticlock():
   for j in range(4):
       for i in range(4):
          GPIO.output(motorPin[i],0x99<<j & (0x80>>i))  
          sleep(stepSpeed)
   return redirect(url_for('stream'))

@app.route('/buzzer_on')
def buzzer_on():
    subprocess.call('./buzzer_on')
    time.sleep(0.1)
    return redirect(url_for('stream'))

@app.route('/buzzer_off')
def buzzer_off():
    subprocess.call('./buzzer_off')
    return redirect(url_for('stream'))

def sigint_handler(signal, frame):
    app.logger.debug("Closing")
    GPIO.cleanup()
    app.logger.debug("Closed")
    sys.exit(0)

if __name__ == "__main__":
    setup() 
    signal.signal(signal.SIGINT, sigint_handler)
    pi = pigpio.pi()
    app.debug = True
    app.run(host="localhost", port=5000)

