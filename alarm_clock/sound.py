"""Sound backend. winsound is stdlib on Windows; everywhere else we fall
back to the terminal bell so the tool still works without extra deps."""
import sys
import time


def play_sound() -> None:
    if sys.platform == "win32":
        import winsound

        winsound.Beep(1000, 400)
    else:
        print("\a", end="", flush=True)
        time.sleep(0.4)
