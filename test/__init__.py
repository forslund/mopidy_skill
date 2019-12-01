from unittest import mock

from test.integrationtests.skills.skill_tester import SkillTest


def test_runner(skill, example, emitter, loader):
    s = [s for s in loader.skills if s and s.root_dir == skill][0]
    s.mopidy = mock.MagicMock()
    s.playlist = {
        'Armikrog OST': {'type': 'album', 'uri': 'file:///track.mp3'}
    }
    ret = SkillTest(skill, example, emitter).run(loader)
    if example.endswith('start.json'):
        s.mopidy.play.assert_called_with()

    return ret
