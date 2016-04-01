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

# The location of this script.
my $callback_url = "http://exobrain.pjf.id.au:3001/rickroll";

# Played on timeout.
my $goodbye = "Thank you for calling the National Rick Astley Hotline. Goodbye.";

# Tune selections

my $original = {
    description => "The Original",
    by => "Rick Astley",
    url => "https://dl.dropboxusercontent.com/u/9702672/music/01-NeverGonnaGiveYouUp.mp3",
};

# TODO: I originally made this a hash so "original" could be 9, but
# it's kinda a pain in the ass, so at some point we should make this
# an array with auto-numbering.
my %tunes = (
    1 => {
        # https://www.youtube.com/watch?v=b1WWpKEPdT4
        description => "Eight bit",
        by => "Kita Khyber",
        url => "https://dl.dropboxusercontent.com/u/9702672/music/8-Bit%20Rick%20Roll.mp3",
    },
    2 => {
        # https://www.youtube.com/watch?v=q-9KqwCFDJs
        description => "Dubstep",
        by => "Crystalize",
        url => "https://dl.dropboxusercontent.com/u/9702672/music/Rick-Astley-Dubstep.mp3",
    },
    3 => {
        # Not sure who this is by
        # https://vimeo.com/64322245
        description => "Daft Punk",
        url => "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Roll%20Never%20Gonna%20Give%20You%20Up%20%28Daft%20Punk%20remix%29.mp3",
    },
    4 => {
        # Avicii, but Twilio gets confused by that.
        # https://www.youtube.com/watch?v=oT3mCybbhf0
        description => "Uh-vee-chee",
        by => "Nils",
        url => "https://dl.dropboxusercontent.com/u/9702672/music/AVICII%20and%20RICK%20ASTLEY%20-%20Never%20Gonna%20Wake%20Up%20%28Mashup-Remix%29.mp3",
    },
    5 => {
        # https://www.youtube.com/watch?v=Eupg7rZ9AUY
        description => "Drum and bass",
        by => "Wave-shapers",
        url => "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Astley%20-%20Never%20Gonna%20Give%20You%20Up%20%28WAV35HAPERS%20Remix%29.mp3",
    },
    6 => {
        # https://www.youtube.com/watch?v=KykFbfCMizo
        description => "E.D.M.",
        by => "Riot", # R!OT
        url => "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Astley%20-%20Never%20Gonna%20Give%20You%20Up%20%28R%21OT%20Remix%29.mp3",
    },
    7 => {
        # https://www.youtube.com/watch?v=GL-8XuoxuaQ
        description => "Metal",
        by => "Andy Rehfeldt",
        url => "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Astley-Never%20Gonna%20Give%20You%20Up%28Metal%20Version%29.mp3",
    },
    8 => {
        # https://www.youtube.com/watch?v=snC4ZtW9dHI
        description => "Nirvana",
        by => "i. v. lad e. o", # ivladeo
        url => "https://dl.dropboxusercontent.com/u/9702672/music/Rick%20Astley%20%20%20Nirvana%20Mashup%20%20%20Never%20gonna%20give%20your%20teen%20spirit%20up.mp3",
    },

    9 => $original,

    # Zero is menu! ^_^
);

# Prep work, prepare our menu.

my $menu = "Welcome to the national Rick Astley hotline. You may make your selection at any time.\n";

foreach my $key (sort keys %tunes) {
    my $artist = $tunes{$key}{by} || "unknown";
    $menu .= "To listen to $tunes{$key}{description} by $artist, press $key.\n";
}

$menu .= "To hear these options again, press zero.\n";
$menu .= "If you do not wish to be rick-rolled, please hang up now.";

# This is a regexp, as there may be a leading path in our URL.
any qr{.*/rickroll} => sub {

    my $selection = param "Digits";

    # No selection is a first-time caller. Give them the classic rick.
    if (not defined $selection) {
        return PlayTune($original);
    }

    # Play a tune selection, if we have one.
    elsif (my $tune = $tunes{$selection}) {
        return PlayTune($tune);
    }

    # Otherwise play our menu.
    return Menu();

};

any '/sms' => sub {
    warn Dumper params();
    return Twilio("");
};

dance;

func PlayTune($tune) {
    return Twilio( Gather($callback_url, Play($tune->{url}), Say($menu) ), Say($goodbye) );
}

sub Menu {
    return Twilio( Gather($callback_url, Say($menu) ), Say($goodbye) );
}

sub Say    { return qq{<Say>@_</Say>}                     }
sub Play   { return qq{<Play loop="1">@_</Play>}          }
sub Record { return qq{<Record action="@_" />}            }

func Pause($seconds = 1) {
    return qq{<Pause length="$seconds"/>}
}

func Gather($url!, @args) { 
    return qq{<Gather numDigits="1" timeout="10" action="$url">@args</Gather>} 
}

func Redirect($url!, $method = "GET") {
    return qq{<Redirect method="$method">/$url</Redirect>\n};
}

sub Twilio {
    return qq{<?xml version="1.0" encoding="UTF-8" ?>\n<Response>@_</Response>};
}

