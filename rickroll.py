from flask import Flask, request
app = Flask(__name__)

from twilio import twiml
from six.moves.urllib.parse import quote
import yaml

with open('songs.yaml') as f:
    yaml_content = yaml.safe_load(f.read())

tunes = [yaml_content[song] for song in yaml_content['remixes']]
tunes.insert(0, None)  # Zero is always the menu.
tunes.append(yaml_content['original'])  # Make sure we add in the original.

# Played on timeout
goodbye = "Thank you for calling the National Rick Astley Hotline. Goodbye."

def play_tune(tune):
    """Takes a tune dictionary, returns a TwiML response that plays it."""

    # If somehow we're called with no argument, which could happen if we had
    # a short menu or multi-key input.
    if tune is None:
        return play_menu()

    response = twiml.Response()

    # By calling functions on gather, digits can be pressed during the song
    # playback *and* the menu afterwards.
    gather = response.gather(numDigits=1, timeout=10)
    gather.play(yaml_content['url_base'] + quote(tune['filename']))
    gather.say(generate_menu())
    
    # Our goodbye triggers after gather times out.
    response.say(goodbye)

    return response

def play_menu():
    """Plays the menu"""

    response = twiml.Response()

    gather = response.gather(numDigits=1, timeout=10)
    gather.say(generate_menu())

    response.say(goodbye)

    return response

@app.route("/", methods = ['GET','POST'])
def original():

    selection = request.values.get('Digits')

    # Without a selection, play the original
    if selection is None:
        return str(play_tune(yaml_content['original']))

    # With a selection try to turn into an index we can use.
    # There may be a '#' or '*', so we'll default to '0'
    # (our menu) if we fail to parse as an int
    try:
        selection = int(selection)
    except ValueError:
        selection = 0

    # Zero is always our menu.
    if selection == 0:
        return str(play_menu())

    # Otherwise load the song they want, with a default of the original
    # song if they select something outsie our array bounds.
    tune = yaml_content['original']

    try: tune = tunes[selection]
    except Exception: pass

    return str(play_tune(tune))

def generate_menu():
    menu = "Welcome to the national Rick Astley hotline. You may make your selection at any time.\n"

    for idx, song in enumerate(tunes):

        if song is None:
            continue

        menu += "To listen to {}".format(song['title'])

        if 'artist' in song:
            menu += " by {}".format(song['artist'])

        menu += ", press {}.\n".format(idx)

    menu += "To hear these options again, press zero.\n"
    menu += "If you do not wish to be rick-rolled again, please hang up now."

    return menu

if __name__ == "__main__":
    app.run()
