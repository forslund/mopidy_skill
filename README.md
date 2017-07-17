Mopidy Skill
=====================

A small skill for playing music with the help of the mopidy music server. Currently the skill supports spotify, local music and google music. The skill is setup to play albums, playlists genres or artists.

### Requirements

This skill require mopidy and some related packages to function:

- libspotify
- mopidy
- mopidy-spotify
- mopidy-local-mysql

Most of these requirements can be installed through the standard method for the OS. The exception is libspotify that must be retrieved from spotify. I recommend using the official [mopidy install guide](https://docs.mopidy.com/en/latest/installation/) to get the software for your specific system.

### Install skills

Use `msm install mopidy_skill` or clone the *mopidy_skill* repository

```
git clone http://github.com/forslund/mopidy_skill.git
```

into `mycroft/mycroft/skills` directory or your directory for third party skills (`~/.mycroft/third_party_skills/` by default)

### Mopidy Setup

Mopidy configuration is complex and this description will only touch the areas that are relevant for the skill.

Mopidy settings are made in *~/.config/mopidy/mopidy.conf* for a desktop install and under */etc/mopidy/mopidy.conf* for picroft/Mark-1 (if it doesn't exist it needs to be created).

Below the basic configuration needed is listed, for more details check out the official documentation at https://www.mopidy.com

#### Spotify

Under the heading

`[spotify] `

make sure the following parameters are entered

```
enabled=true
username=USERNAME
password=PASSWORD
client_id = ... client_id value you got from mopidy.com
client_secret = ... client_secret value you got from mopidy.com
```

`client_id` and `client_secret` can be generated at https://www.mopidy.com/authenticate/#spotify

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

### Mycroft Setup

Mycroft needs to be pointed to the mopidy server. Add the following to `~/.mycroft/mycroft.conf` for a local mopidy server at the default port:

```json
  "Mopidy Skill": {
    "mopidy_url" = "http://localhost:6680"
  }
```

### Running the skill

Before starting mycroft, *mopidy* should be launched.

Easies way is to open a terminal and simply run

```
mopidy
```

## Usage

**spotify**
- The skill collects the playlists from the user and will play them if requested. Spotify can also be searched for albums
examples:

`play discover weekly`

`search spotify for Hello Nasty`

**local music**
- the local music skill browses the local media directory and adds each artist, album and genre found as a play intent.

examples:

`play Armikrog OST`

`play something by Terry Scott Taylor`

`play rock music`

**gmusic**
- Gmusic works in much the same way as the local music.
