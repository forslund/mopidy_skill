# <img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/music.svg' card_color='#FF0004' width='50' height='50' style='vertical-align:bottom'/> 
Play music via your Mopidy Server

## About
Mopidy is an extensible stand alone music server handling music libraries and remote services alike. This skill interfaces with the server through the REST api.

### Mycroft Setup

Mycroft needs to be pointed to the mopidy server, this is easily done using the skill settings page on Mycroft-Home. By default it will try to connect to a mopidy server on localhost.

### Mopidy Setup

I recommend using the official [mopidy install guide](https://docs.mopidy.com/en/latest/installation/) to get the software for your specific system.

In addition to the base installation of mopidy the skill REQUIRES the local-mysql plugin to fetch the metadata from the local library and should be able to use the data from the `mopidy-gmusic` plugin.

Mopidy configuration is complex and this description will only touch the areas that are relevant for the skill. Mopidy settings are made in *~/.config/mopidy/mopidy.conf* for a desktop install and under */etc/mopidy/mopidy.conf* for picroft/Mark-1 (if it doesn't exist it needs to be created).

This readme only covers the basics, for more details check out the official documentation at https://www.mopidy.com

#### Local music

For playing music from the local file system or file share check under the heading

` [local] `

and make sure the following config options are set according to your system

```
enabled = true
library = sqlite
media_dir = PATH_TO_YOUR_MUSIC
```

after this is done scan the local collection by running

` mopidy local scan `


## Examples
* "play Armikrog OST"
* "play something by Terry Scott Taylor"
* "play rock music"

## Credits
@forslund

## Category
**Music**

## Tags
#mopidy
#music
