import arcade

from triple_vision import Settings as s
from triple_vision.networking import client
from triple_vision.views import LoginView


def main() -> None:
    window = arcade.Window(*s.WINDOW_SIZE, s.TITLE)
    view = LoginView()

    client.connect()

    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
