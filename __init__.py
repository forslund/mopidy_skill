import re
import time
from fuzzywuzzy.process import extractOne as extract_one

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

from .mopidypost import Mopidy


NOTHING_FOUND = (None, 0.0)


class MopidySkill(CommonPlaySkill):
    def __init__(self):
        super(MopidySkill, self).__init__('Mopidy Skill')
        self.mopidy = None
        self.volume_is_low = False
        self.regexes = {}

    def _connect(self):
        url = 'http://localhost:6680'
        if self.settings:
            url = self.settings.get('mopidy_url', url)

        try:
            mopidy = Mopidy(url)
        except Exception:
            self.log.warning('Could not connect to Mopidy server')
            return None

        self.log.info('Connected to mopidy server')
        self.cancel_scheduled_event('MopidyConnect')
        self.albums = {}
        self.artists = {}
        self.genres = {}
        self.playlists = {}
        self.radios = {}
        self.track_names = {}

        self.log.info('Loading content')
        self.albums['gmusic'] = mopidy.get_gmusic_albums()
        self.artists['gmusic'] = mopidy.get_gmusic_artists()
        self.genres['gmusic'] = mopidy.get_gmusic_radio()
        self.playlists['gmusic'] = {}
        self.track_names['gmusic'] = {}

        self.albums['local'] = mopidy.get_local_albums()
        self.artists['local'] = mopidy.get_local_artists()
        self.genres['local'] = mopidy.get_local_genres()
        self.playlists['local'] = mopidy.get_local_playlists()
        self.track_names['local'] = mopidy.get_local_track_names()

        self.albums['spotify'] = {}
        self.artists['spotify'] = {}
        self.genres['spotify'] = {}
        self.playlists['spotify'] = mopidy.get_spotify_playlists()
        self.track_names['spotify'] = {}

        self.playlist = {}
        for loc in ['local', 'gmusic', 'spotify']:
            self.log.info(loc)
            self.playlist.update(self.playlists[loc])
            self.log.info(loc)
            self.playlist.update(self.genres[loc])
            self.log.info(loc)
            self.playlist.update(self.artists[loc])
            self.log.info(loc)
            self.playlist.update(self.albums[loc])
            self.log.info(loc)
            self.playlist.update(self.track_names[loc])

        return mopidy

    def initialize(self):
        self.log.info('initializing Mopidy skill')
        super(MopidySkill, self).initialize()

        # Setup handlers for playback control messages
        self.add_event('mycroft.audio.service.next', self.handle_next)
        self.add_event('mycroft.audio.service.prev', self.handle_prev)
        self.add_event('mycroft.audio.service.pause', self.handle_pause)
        self.add_event('mycroft.audio.service.resume', self.handle_resume)

        self.mopidy = self._connect()

    def play(self, tracks):
        self.mopidy.clear_list()
        self.mopidy.add_list(tracks)
        self.mopidy.play()

    def translate_regex(self, regex):
        if regex not in self.regexes:
            path = self.find_resource(regex + '.regex', 'dialog')
            if path:
                with open(path) as f:
                    string = f.read().strip()
                self.regexes[regex] = string
        return self.regexes[regex]

    def CPS_match_query_phrase(self, phrase):
        # If no mopidy connection can be detected return None
        if self.mopidy is None:
            self.mopidy = self._connect()
            if not self.mopidy:
                return None

        self.log.info('Checking Mopidy for {}'.format(phrase))

        mopidy_specified = 'mopidy' in phrase
        phrase = re.sub(self.translate_regex('on_mopidy'), '', phrase)

        match_level = CPSMatchLevel.MULTI_KEY
        match = self.specific_query(phrase)
        # If nothing was found check for a generic match
        if match == NOTHING_FOUND:
            match = self.generic_query(phrase)
            match_level = CPSMatchLevel.GENERIC

        self.log.info('Mopidy match: {}'.format(match))
        if match == NOTHING_FOUND:
            self.log.debug('Nothing found on mopidy')
            return None
        else:
            return (phrase,
                    (CPSMatchLevel.EXACT if mopidy_specified else match_level),
                    {'playlist': match[0],
                     'playlist_type': match[2],
                     'library_type': match[3]
                     })


    def query_song(self, song):
        best_found = None
        best_conf = 0
        library_type = None
        for t in self.track_names:
            found, conf = (extract_one(song, self.track_names[t].keys()) or
                           (None, 0))
            if conf > best_conf and conf > 50:
                best_conf = conf
                best_found = found
                library_type = t
        return best_found, best_conf, 'song', library_type


    def query_artist(self, artist):
        best_found = None
        best_conf = 0.0
        library_type = None
        for t in self.artists:
            found, conf = (extract_one(artist, self.artists[t].keys()) or
                           (None, 0))
            if conf > best_conf and conf > 50:
                best_conf = conf
                best_found = found
                library_type = t
        return best_found, best_conf, 'artist', library_type

    def query_album(self, album):
        best_found = None
        best_conf = 0
        library_type = None
        for t in self.albums:
            self.log.info(self.albums[t].keys())
            found, conf = (extract_one(album, self.albums[t].keys()) or
                           (None, 0))
            if conf > best_conf and conf > 50:
                best_conf = conf
                best_found = found
                library_type = t
        self.log.info('ALBUMS')
        self.log.info((best_found, best_conf))
        return best_found, best_conf, 'album', library_type

    def specific_query(self, phrase):
        """Check if the request is for a specific type.

        This checks, albums, artists, genres and tracks.
        """
        # Check if playlist
        #match = re.match(self.translate_regex('playlist'), phrase)
        #if match:
        #    return self.query_playlist(match.groupdict()['playlist'])

        # Check album
        match = re.match(self.translate_regex('album'), phrase)
        if match:
            album = match.groupdict()['album']
            return self.query_album(album)

        # Check artist
        match = re.match(self.translate_regex('artist'), phrase)
        if match:
            artist = match.groupdict()['artist']
            return self.query_artist(artist)
        match = re.match(self.translate_regex('song'), phrase)
        if match:
            song = match.groupdict()['track']
            return self.query_song(song)
        return NOTHING_FOUND

    def generic_query(self, phrase):
        found, conf = extract_one(phrase, self.playlist.keys())
        if conf > 50:
            return found, conf, 'generic', ''
        else:
            return NOTHING_FOUND

    def CPS_start(self, phrase, data):
        p = data.get('playlist')
        list_type = data.get('playlist_type', 'generic')
        library_type = data.get('library_type', 'generic')

        lists = {'generic': self.playlist,
                 'artist': self.artists,
                 'album': self.albums,
                 'song': self.track_names
                 }
        if list_type == 'generic':
            playlists = lists[list_type]
        else:
            playlists = lists[list_type][library_type]
        self.stop()
        self.speak('Playing {}'.format(p))
        time.sleep(3)
        if playlists[p]['type'] == 'playlist':
            tracks = self.mopidy.get_items(playlists[p]['uri'])
        if playlists[p]['type'] == 'track':
            tracks = playlists[p]['uri']
        else:
            tracks = self.mopidy.get_tracks(playlists[p]['uri'])
        self.play(tracks)

    def stop(self, message=None):
        self.log.info('Handling stop request')
        if self.mopidy:
            self.mopidy.clear_list()
            self.mopidy.stop()

    def handle_next(self, message):
        self.mopidy.next()

    def handle_prev(self, message):
        self.mopidy.previous()

    def handle_pause(self, message):
        self.mopidy.pause()

    def handle_resume(self, message):
        """Resume playback if paused"""
        self.mopidy.resume()

    def lower_volume(self, message):
        self.log.info('lowering volume')
        self.mopidy.lower_volume()
        self.volume_is_low = True

    def restore_volume(self, message):
        self.log.info('maybe restoring volume')
        self.volume_is_low = False
        time.sleep(2)
        if not self.volume_is_low:
            self.log.info('restoring volume')
            self.mopidy.restore_volume()

    def handle_currently_playing(self, message):
        current_track = self.mopidy.currently_playing()
        if current_track is not None:
            self.mopidy.lower_volume()
            time.sleep(1)
            if 'album' in current_track:
                data = {'current_track': current_track['name'],
                        'artist': current_track['album']['artists'][0]['name']}
                self.speak_dialog('currently_playing', data)
            time.sleep(6)
            self.mopidy.restore_volume()


def create_skill():
    return MopidySkill()
