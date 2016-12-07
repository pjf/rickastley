from flask import Flask
app = Flask(__name__)

from twilio import twiml

_original = {
    'description': "The Original",
    'by': "Rick Astley",
    'url': "https://dl.dropboxusercontent.com/u/9702672/music/01-NeverGonnaGiveYouUp.mp3"
}

tunes = [
    None,   # Zero is always the menu
    {
        'src': "https://www.youtube.com/watch?v=b1WWpKEPdT4",
        'description': "Eight bit",
        'by': "Kita Khyber",
        'url': "https://dl.dropboxusercontent.com/u/9702672/music/8-Bit%20Rick%20Roll.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=q-9KqwCFDJs",
        'description': "Dubstep",
        'by': "Crystalize",
        'url': "https://dl.dropboxusercontent.com/u/9702672/music/Rick-Astley-Dubstep.mp3",
    },
    {
        # Not sure who this is by
        'src': "https://vimeo.com/64322245",
        'description': "Daft Punk",
        'url': "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Roll%20Never%20Gonna%20Give%20You%20Up%20%28Daft%20Punk%20remix%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=oT3mCybbhf0",
        'description': "Uh-vee-chee",  # Avicii, but Twilio gets confused by that.
        'by': "Nils",
        'url': "https://dl.dropboxusercontent.com/u/9702672/music/AVICII%20and%20RICK%20ASTLEY%20-%20Never%20Gonna%20Wake%20Up%20%28Mashup-Remix%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=Eupg7rZ9AUY",
        'description': "Drum and bass",
        'by': "Wave-shapers",
        'url': "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Astley%20-%20Never%20Gonna%20Give%20You%20Up%20%28WAV35HAPERS%20Remix%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=KykFbfCMizo",
        'description': "E.D.M.",
        'by': "Riot", # R!OT
        'url': "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Astley%20-%20Never%20Gonna%20Give%20You%20Up%20%28R%21OT%20Remix%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=GL-8XuoxuaQ",
        'description': "Metal",
        'by': "Andy Rehfeldt",
        'url': "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Astley-Never%20Gonna%20Give%20You%20Up%28Metal%20Version%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=snC4ZtW9dHI",
        'description': "Nirvana",
        'by': "i. v. lad e. o", # ivladeo
        'url': "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Astley%20%20%20Nirvana%20Mashup%20%20%20Never%20gonna%20give%20your%20teen%20spirit%20up.mp3",
    },
    _original
]

# Menu generation. I'd love to put this in its own function to be clean and
# tidy, but if I put that at the end Python gets grumpy and I'm not sure how to
# forward-declare. I could put it into a separate file and include that, but
# then I have to learn how file inclusion works. ;)

menu = "Welcome to the national Rick Astley hotline. You may make your selection at any time.\n"

for idx, song in enumerate(tunes):

    if song is None:
        continue

    menu += "To listen to {}".format(song['description'])

    if 'by' in song:
        menu += " by {}".format(song['by'])

    menu += ", press {}.\n".format(idx)

menu += "To hear these options again, press zero.\n"
menu += "If you do not wish to be rick-rolled, please hang up now."

@app.route("/")
def original():
    response = twiml.Response()

    gather = response.gather(numDigits=1, timeout=10)
    gather.play(_original['url'])

    response.say(menu)

    return str(response)


if __name__ == "__main__":
    app.run()
