import unittest
from unittest.mock import patch, MagicMock
import pygame
from audio import AudioManager  

class TestAudioManager(unittest.TestCase):
    @patch("pygame.mixer.init")
    @patch("pygame.mixer.Sound")
    def setUp(self, mock_sound, mock_mixer_init):
        """Setup a mock AudioManager instance."""
        self.audio_manager = AudioManager()
    
    def test_audio_dict_contains_expected_keys(self):
        """Test that all expected sound keys are in audio_dict."""
        expected_keys = {
            "startMLSound", "stopMLSound", "walkMode", "pushUpsMode",
            "legControlMode", "gyroMode", "machineLearningMode", "danceMode",
            "song1", "song2", "song3", "song4", "startup1", "startup2",
            "pause", "error"
        }
        self.assertEqual(set(self.audio_manager.audio_dict.keys()), expected_keys)

    @patch("pygame.mixer.Sound.play")
    def test_play_sound_valid_key(self, mock_play):
        """Test that play_sound calls pygame.mixer.Sound.play for a valid key."""
        self.audio_manager.play_sound("song1")
        mock_play.assert_called_once()

    @patch("pygame.mixer.Sound.play")
    def test_play_sound_invalid_key(self, mock_play):
        """Test that play_sound does not call pygame.mixer.Sound.play for an invalid key."""
        self.audio_manager.play_sound("invalid_key")
        mock_play.assert_not_called()

    @patch("pygame.mixer.Sound.play")
    def test_play_mode_sounds_valid_mode(self, mock_play):
        """Test that play_mode_sounds calls play_sound with correct mode."""
        self.audio_manager.play_mode_sounds(2)  # Should map to "legControlMode"
        mock_play.assert_called_once()

    @patch("pygame.mixer.Sound.play")
    def test_play_mode_sounds_invalid_mode(self, mock_play):
        """Test that play_mode_sounds does not call play_sound for an invalid mode."""
        self.audio_manager.play_mode_sounds(99)  # No mapping for mode 99
        mock_play.assert_not_called()

    @patch("pygame.mixer.Sound.play")
    @patch("random.choice", return_value="song3")
    def test_play_songs_random(self, mock_choice, mock_play):
        """Test that play_songs with -1 selects a random song and plays it."""
        self.audio_manager.play_songs(-1)
        mock_choice.assert_called_once()
        mock_play.assert_called_once()

    @patch("pygame.mixer.Sound.play")
    def test_play_songs_specific_song(self, mock_play):
        """Test that play_songs plays the correct song for a valid index."""
        self.audio_manager.play_songs(2)  # Should map to "song2"
        mock_play.assert_called_once()

    @patch("pygame.mixer.Sound.play")
    def test_play_songs_invalid_song(self, mock_play):
        """Test that play_songs does not call play_sound for an invalid song index."""
        self.audio_manager.play_songs(99)  # No mapping for song99
        mock_play.assert_not_called()

if __name__ == "__main__":
    unittest.main()
