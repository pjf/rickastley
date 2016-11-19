from flask import Flask
app = Flask(__name__)

from twilio import twiml

orig_song = "https://dl.dropboxusercontent.com/u/9702672/music/01-NeverGonnaGiveYouUp.mp3"
menu     = "Menu disabled in development."

@app.route("/")
def original():
    response = twiml.Response()

    gather = response.gather(numDigits=1, timeout=10)
    gather.play(orig_song)

    response.say(menu)

    return str(response)

if __name__ == "__main__":
    app.run()
