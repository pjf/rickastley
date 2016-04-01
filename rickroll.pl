#!/usr/bin/perl -w
use 5.010;
use strict;
use warnings;
use autodie;
use Method::Signatures;

use Dancer;
use Data::Dumper;

set port => 3001;
set logger => 'console';
set log => 'core';
set warnings => 1;

any '/rickroll' => sub {
    Twilio(Play('https://dl.dropboxusercontent.com/u/9702672/music/01-NeverGonnaGiveYouUp.mp3'));
};

any '/sms' => sub {
    warn Dumper params();
    return Twilio("");
};

dance;

sub Say    { return qq{<Say>@_</Say>}                     }
sub Play   { return qq{<Play loop="1">@_</Play>}          }
sub Record { return qq{<Record action="@_" />}            }

func Pause($seconds = 1) {
    return qq{<Pause length="$seconds"/>}
}

func Gather($url!, @args) { 
    return qq{<Gather numDigits="1" action="/$url">@args</Gather>} 
}

func Redirect($url!, $method = "GET") {
    return qq{<Redirect method="$method">/$url</Redirect>\n};
}

sub Twilio {
    return qq{<?xml version="1.0" encoding="UTF-8" ?>\n<Response>@_</Response>};
}

