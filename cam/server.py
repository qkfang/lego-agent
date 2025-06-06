from flask import Flask, render_template, Response
from flask_cors import CORS
from streamer import Streamer

app = Flask(__name__)
CORS(app)

streamer = Streamer('192.168.0.50', 8080)
streamer.start()

def gen():

  while True:
    if streamer.streaming:
      yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + streamer.get_jpeg() + b'\r\n\r\n')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/video_feed')
def video_feed():
  return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/photo')
def photo():
    if streamer.streaming and streamer.get_jpeg():
        return Response(streamer.get_jpeg(), mimetype='image/jpeg')
    
if __name__ == '__main__':
  app.run(host='192.168.0.50', threaded=True)
