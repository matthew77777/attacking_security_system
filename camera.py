# camera.py

import cv2

class Camera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        #frame = cv2.flip()
        image = cv2.flip(image,-1)
        ret, frame = cv2.imencode('.jpg', image)
        return frame


