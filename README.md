# National Rick Astley Hotline

You're welcome, Internet.

- Australia: +61-3-8652-1453
- New Zealand: +64-9-886-0565
- UK: +44-11-7325-7425
- USA: +1-760-706-7425

Want me to continue bringing whimsy to the world? [Support me on Patreon](https://www.patreon.com/_pjf).

You can also [become a fan on Facebook](https://www.facebook.com/full.commitment).

# Technical details

The National Rick Astley Hotline brings joy to thousands of people each year. It uses the following software stack:

- [Twilio](https://www.twilio.com/) for the front-end numbers.
- [Flask](http://flask.pocoo.org/) for running the microserver that handles requests from Twilio.
- [Zappa](https://github.com/Miserlou/Zappa) for deploying the flask app to AWS/Lambda.

## Running this code

First, set up your virtual environment and install the requirements:

    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt

To run, simply:

    $ . venv/env/activate   # If not already in your venv
    $ python rickroll.py

This runs the flask server on a local port, so you can poke around with it.

The [flask quickstart](http://flask.pocoo.org/docs/0.11/quickstart/) explains how you can
run flask on a public server, at which point you can point a Twilio webhook at your server
and you've built your own hotline!

## Deploying with Zappa

The main service runs using [AWS Lambda](https://aws.amazon.com/documentation/lambda/), a
scalable, serverless platform which removes the overhead of needing to maintain an underlying
server. The [Zappa documentation](https://github.com/Miserlou/Zappa#zappa---serverless-python-web-services)
provides detailed set-up instructions, but if you have your `~/.aws/credentials` file in order,
it should be as simple as:

    $ . venv/bin/activate
    $ zappa init
    $ zappa deploy

Record the URL it spits out, connect it as a webhook to your own phone number with Twilio, and you have your own serverless Rick Astley Hotline!

## How much do you spend bringing joy to Rick Astley fans?

As of mid 2018, connection costs were averaging about $900 USD/yr. It's totally
worth it for the joy it brings others.

If you want to defray my hosting costs, there's always [bitcoin](https://blockchain.info/address/18pgvfqWGs2CvurmNvq58h499RRTPCh3mz) and [Patreon](https://www.patreon.com/_pjf).

