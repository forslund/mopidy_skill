Mycroft Media Skills
=====================

### Requirements

These media skills currently requires some external software to work.

- libspotify
- mopidy
- mopidy-spotify
- mopidy-local-mysql

Most of these requirements can be installed through the standard method for the OS. The exception is libspotify that must be retrieved from spotify. I recommend using the official [mopidy install guide](https://docs.mopidy.com/en/latest/installation/) to get the software for your specific system.

### Install skills

Clone the *mopidy_skill* repository

```
git clone http://github.com/forslund/mopidy_skill.git
```

and copy desired skills to the `mycroft/mycroft/skills` directory or your directory for third party skills (`~/.mycroft/third_party_skills/` by default)

### Mopidy Setup

in *~/.config/mopidy/mopidy.conf* (if it doesn't exist it needs to be created) under

`[spotify] `

```
enabled=true
username=USERNAME
password=PASSWORD
```

and under
` [local] `

```
enabled = true
library = sqlite
media_dir = PATH_TO_YOUR_MUSIC
```

after this is done scan the local collection by running

` mopidy local scan `

### Mycroft Setup

Mycroft needs to be pointed to the mopidy server. Add the following to `~/.mycroft/mycroft.ini` for a local mopidy server at the defualt port:

```
[Mopidy Skill]
mopidy_url = http://localhost:6680
```

### Running the skills

The skills will now be started together with mycroft but before starting mycroft *mopidy* should be launched.

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
