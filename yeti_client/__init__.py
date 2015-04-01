from models import Config

__version__ = "0.5"
VERSION = __version__

CLIENT_NAME = 'YETI Web Client'

ENABLE_ALERT_VIEWER = False

# Function that gets called once when Django starts
def startup():
    try:
        config = Config.objects.get()
        config.polling = False
        config.save()
    except:
        pass

startup()