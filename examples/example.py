from audiobackend import AudioBackend
import time

def create_music_player():
    player = AudioBackend()

    def format_time(ms):
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes}:{seconds:02d}"

    def update_position(pos):
        print(f"\rPosition: {format_time(pos)}", end="")

    player.set_position_callback(update_position)

    return player

# Usage
player = create_music_player()
player.load_file("music.flac")
player.play()

# Keep program running
try:
    while player.is_playing:
        time.sleep(0.1)
except KeyboardInterrupt:
    player.stop()