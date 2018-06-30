import sys
from os.path import dirname, abspath, basename

from adapt.intent import IntentBuilder
from mycroft.messagebus.message import Message

import time
import requests
from os.path import dirname
from mycroft.util.log import LOG
import subprocess

from .mopidypost import Mopidy
from .media import MediaSkill


class MopidySkill(MediaSkill):
    def __init__(self):
        super(MopidySkill, self).__init__('Mopidy Skill')
        self.mopidy = None
        self.volume_is_low = False
        self.connection_attempts = 0
        subprocess.call(['mopidy', 'local', 'scan'])
        self.process = subprocess.Popen(['mopidy'])

    def _connect(self, message):
        url = 'http://localhost:6680'
        if self.base_conf:
            url = self.base_conf.get('mopidy_url', None)
        if self.config:
            url = self.config.get('mopidy_url', url)
        try:
            self.mopidy = Mopidy(url)
        except:
            if self.connection_attempts < 1:
                LOG.debug('Could not connect to server, will retry quietly')
            self.connection_attempts += 1
            time.sleep(10)
            self.emitter.emit(Message(self.name + '.connect'))
            return

        LOG.info('Connected to mopidy server')
        self.albums = {}
        self.artists = {}
        self.genres = {}
        self.playlists = {}
        self.radios = {}

        LOG.info('Loading content')
        self.albums['gmusic'] = self.mopidy.get_gmusic_albums()
        self.artists['gmusic'] = self.mopidy.get_gmusic_artists()
        self.genres['gmusic'] = self.mopidy.get_gmusic_radio()
        self.playlists['gmusic'] = {}

        self.albums['local'] = self.mopidy.get_local_albums()
        self.artists['local'] = self.mopidy.get_local_artists()
        self.genres['local'] = self.mopidy.get_local_genres()
        self.playlists['local'] = self.mopidy.get_local_playlists()

        self.albums['spotify'] = {}
        self.artists['spotify'] = {}
        self.genres['spotify'] = {}
        self.playlists['spotify'] = self.mopidy.get_spotify_playlists()

        self.playlist = {}
        for loc in ['local', 'gmusic', 'spotify']:
            LOG.info(loc)
            self.playlist.update(self.playlists[loc])
            LOG.info(loc)
            self.playlist.update(self.genres[loc])
            LOG.info(loc)
            self.playlist.update(self.artists[loc])
            LOG.info(loc)
            self.playlist.update(self.albums[loc])

        self.register_vocabulary(self.name, 'NameKeyword')
        for p in self.playlist.keys():
            LOG.debug("Playlist: " + p)
            self.register_vocabulary(p, 'PlaylistKeyword' + self.name)
        intent = IntentBuilder('PlayPlaylistIntent' + self.name)\
            .require('PlayKeyword')\
            .require('PlaylistKeyword' + self.name)\
            .build()
        self.register_intent(intent, self.handle_play_playlist)
        intent = IntentBuilder('PlayFromIntent' + self.name)\
            .require('PlayKeyword')\
            .require('PlaylistKeyword')\
            .require('NameKeyword')\
            .build()
        self.register_intent(intent, self.handle_play_playlist)

        intent = IntentBuilder('SearchSpotifyIntent' + self.name)\
            .require('SearchKeyword')\
            .require('Source')\
            .require('SpotifyKeyword')\
            .build()
        self.register_intent(intent, self.search_spotify)

    def initialize(self):
        LOG.info('initializing Mopidy skill')
        super(MopidySkill, self).initialize()
        self.load_data_files(dirname(__file__))

        self.emitter.on(self.name + '.connect', self._connect)
        self.emitter.emit(Message(self.name + '.connect'))

    def play(self, tracks):
        self.mopidy.clear_list()
        self.mopidy.add_list(tracks)
        self.mopidy.play()

    def handle_play_playlist(self, message):
        p = message.data.get('PlaylistKeyword' + self.name)
        self.before_play()
        self.speak("Playing " + str(p))
        time.sleep(3)
        if self.playlist[p]['type'] == 'playlist':
            tracks = self.mopidy.get_items(self.playlist[p]['uri'])
        else:
            tracks = self.mopidy.get_tracks(self.playlist[p]['uri'])
        self.play(tracks)

    def stop(self, message=None):
        LOG.info('Handling stop request')
        if self.mopidy:
            self.mopidy.clear_list()
            self.mopidy.stop()

    def handle_next(self, message):
        self.mopidy.next()

    def handle_prev(self, message):
        self.mopidy.previous()

    def handle_pause(self, message):
        self.mopidy.pause()

    def handle_play(self, message):
        """Resume playback if paused"""
        self.mopidy.resume()

    def lower_volume(self, message):
        LOG.info('lowering volume')
        self.mopidy.lower_volume()
        self.volume_is_low = True

    def restore_volume(self, message):
        LOG.info('maybe restoring volume')
        self.volume_is_low = False
        time.sleep(2)
        if not self.volume_is_low:
            LOG.info('restoring volume')
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

    def search_spotify(self, message):
        LOG.info('Search Spotify Intent')
        LOG.info(message.data)
        name = message.data['Source']
        LOG.info(name)
        results = self.mopidy.find_album(name, 'spotify')
        if len(results) > 0:
            tracks = results[0]
        if results is not None:
            LOG.info(results)
            if len(results) > 0:
                self.play(results[0]['uri'])
            else:
                self.speak('couldn\'t find an album matching ' + name)

    def stop_mopidy(self):
        """ Send Terminate signal to librespot if it's running. """
        if self.process and self.process.poll() is None:
            self.process.send_signal(signal.SIGTERM)
            self.process.communicate()  # Communicate to remove zombie
            self.process = None

    def shutdown(self):
        self.stop_mopidy()        


def create_skill():
    return MopidySkill()
