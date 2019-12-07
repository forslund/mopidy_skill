import time
from fuzzywuzzy.process import extractOne as extract_one

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel

from .mopidypost import Mopidy


class MopidySkill(CommonPlaySkill):
    def __init__(self):
        super(MopidySkill, self).__init__('Mopidy Skill')
        self.mopidy = None
        self.volume_is_low = False

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

    def CPS_match_query_phrase(self, phrase):
        if self.mopidy is None:
            self.mopidy = self._connect()
            if not self.mopidy:
                return None

        self.log.info('Checking Mopidy for {}'.format(phrase))
        found, conf = extract_one(phrase, self.playlist.keys())
        if conf > 0.5:
            return (phrase,
                    CPSMatchLevel.GENERIC,
                    {'playlist': found})
        else:
            self.log.info('Nothing found on Mopidy')
            return None

    def CPS_start(self, phrase, data):
        p = data.get('playlist')
        self.stop()
        self.speak('Playing {}'.format(p))
        time.sleep(3)
        if self.playlist[p]['type'] == 'playlist':
            tracks = self.mopidy.get_items(self.playlist[p]['uri'])
        if self.playlist[p]['type'] == 'track':
            tracks = self.playlist[p]['uri']
        else:
            tracks = self.mopidy.get_tracks(self.playlist[p]['uri'])
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
