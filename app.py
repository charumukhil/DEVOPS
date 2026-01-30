import cv2
import os
from datetime import datetime
from flask import Flask, render_template, Response

app = Flask(__name__)

# 1. Create the attendance file if it doesn't exist
if not os.path.exists('attendance.csv'):
    with open('attendance.csv', 'w') as f:
        f.write('Event,Date,Time\n')

def mark_attendance():
    """Logs detection to CSV (prevents spamming by checking seconds)"""
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')
    
    # We only log once per second to keep the file clean
    with open('attendance.csv', 'a+') as f:
        f.seek(0)
        lines = f.readlines()
        last_line = lines[-1] if lines else ""
        if time_str not in last_line:
            f.write(f"Face_Detected,{date_str},{time_str}\n")

def gen_frames():
    # Built-in face detector (Always works on Python 3.13)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    camera = cv2.VideoCapture(0) # 0 is default webcam
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                # 🎨 UI: Blue Box and "Scanning" Text
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0), 2)
                cv2.putText(frame, "STATUS: SCANNING RETINA...", (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
                # Logic: Mark attendance in CSV
                mark_attendance()

            # Encode the frame to display in Browser
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # use_reloader=False prevents the camera from opening twice/crashing
    app.run(debug=True, use_reloader=False)