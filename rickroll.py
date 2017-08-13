from flask import Flask, request
app = Flask(__name__)

from twilio import twiml
from twilio.rest import TwilioRestClient

import boto3
import botocore
import os
from datetime import datetime, timedelta
from raven.contrib.flask import Sentry
sentry = Sentry(app)

s3 = boto3.resource('s3')
bucket = s3.Bucket(os.environ['data_bucket'])
twilio_client = TwilioRestClient(os.environ['twilio_sid'],
                                 os.environ['twilio_token'])

# Where we're storing all our audio files.
url_base = "https://s3-us-west-2.amazonaws.com/true-commitment/"

_original = {
    'description': "The Original",
    'by': "Rick Astley",
    'url': url_base + "01-NeverGonnaGiveYouUp.mp3"
}

# Played on timeout
goodbye = "Thank you for calling the National Rick Astley Hotline. Goodbye."

tunes = [
    None,   # Zero is always the menu
    {
        'src': "https://www.youtube.com/watch?v=b1WWpKEPdT4",
        'description': "Eight bit",
        'by': "Kita Khyber",
        'url': url_base + "8-Bit%20Rick%20Roll.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=q-9KqwCFDJs",
        'description': "Dubstep",
        'by': "Crystalize",
        'url': url_base + "Rick-Astley-Dubstep.mp3",
    },
    {
        # Not sure who this is by
        'src': "https://vimeo.com/64322245",
        'description': "Daft Punk",
        'url': url_base + "Rick%20Roll%20Never%20Gonna%20Give%20You%20Up%20%28Daft%20Punk%20remix%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=oT3mCybbhf0",
        'description': "Uh-vee-chee",  # Avicii, but Twilio gets confused by that.
        'by': "Nils",
        'url': url_base + "AVICII%20and%20RICK%20ASTLEY%20-%20Never%20Gonna%20Wake%20Up%20%28Mashup-Remix%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=Eupg7rZ9AUY",
        'description': "Drum and bass",
        'by': "Wave-shapers",
        'url': url_base + "Rick%20Astley%20-%20Never%20Gonna%20Give%20You%20Up%20%28WAV35HAPERS%20Remix%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=KykFbfCMizo",
        'description': "E.D.M.",
        'by': "Riot", # R!OT
        'url': url_base + "Rick%20Astley%20-%20Never%20Gonna%20Give%20You%20Up%20%28R%21OT%20Remix%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=GL-8XuoxuaQ",
        'description': "Metal",
        'by': "Andy Rehfeldt",
        'url': url_base + "Rick%20Astley-Never%20Gonna%20Give%20You%20Up%28Metal%20Version%29.mp3",
    },
    {
        'src': "https://www.youtube.com/watch?v=snC4ZtW9dHI",
        'description': "Nirvana",
        'by': "i. v. lad e. o", # ivladeo
        'url': url_base + "Rick%20Astley%20%20%20Nirvana%20Mashup%20%20%20Never%20gonna%20give%20your%20teen%20spirit%20up.mp3",
    },
    _original
]

messages = [
    "We're no strangers to love.",
    "You know the rules, and so do I.",
    "A full commitment's what I'm thinking of.",
    "You wouldn't get this from any other guy.",
    "Call me?",
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
    gather.play(tune['url'])
    gather.say(menu)

    # Our goodbye triggers after gather times out.
    response.say(goodbye)

    return response

def play_menu():
    """Plays the menu"""

    response = twiml.Response()

    gather = response.gather(numDigits=1, timeout=10)
    gather.say(menu)

    response.say(goodbye)

    return response

@app.route("/", methods = ['GET','POST'])
def original():

    selection = request.values.get('Digits')

    # Without a selection, play the original
    if selection is None:
        return str(play_tune(_original))

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
    tune = _original

    try: tune = tunes[selection]
    except Exception: pass

    return str(play_tune(tune))

@app.route("/sms", methods=["POST"])
def sms():
    """Adds an incoming SMS to a queue, to reply to later."""
    bucket.put_object(
        Key='queue/{to}/{from_}'.format(to=request.form['To'],
                                        from_=request.form['From']),
        Body='',
    )
    return "Hello world!"

def send_sms():
    """Empties the queue of incoming SMSes, replying to each one."""
    for queue_entry in bucket.objects.filter(Prefix='queue/'):
        _, our_number, their_number = queue_entry.key.split("/")
        state_key = "state/{}/{}".format(our_number, their_number)

        # Find out which message we sent last, if any
        # Error handling taken from https://stackoverflow.com/a/33843019
        try:
            state_obj = s3.Object(
                os.environ['data_bucket'],
                state_key,
            )
            state_obj.load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                last_msg = -1
            else:
                raise
        else:
            last_msg = int(state_obj.get()['Body'].read().decode('utf8'))

        # Send the next one
        next_msg = last_msg + 1
        if next_msg < len(messages):
            twilio_client.messages.create(
                to=their_number,
                from_=our_number,
                body=messages[next_msg],
            )

        # Record which message we just sent in S3
        bucket.put_object(
            Key=state_key,
            Body=str(next_msg),
            Expires=datetime.now() + timedelta(days=7),
        )

        queue_entry.delete()

if __name__ == "__main__":
    app.run()
