from app import app
from pyfladesk import init_gui
from screeninfo import get_monitors

for m in get_monitors():
    pass

if __name__ == "__main__":
    init_gui(app, window_title="Mercadologic Tira-Teima ", width=m.width, height=m.height,
             icon="./app/static/images/favicon.ico")
