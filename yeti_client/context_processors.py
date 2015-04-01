from __init__ import CLIENT_NAME, ENABLE_ALERT_VIEWER, VERSION


def default(request):
    return {
        'VERSION': VERSION,
        'CLIENT_NAME': CLIENT_NAME,
        'ENABLE_ALERT_VIEWER': ENABLE_ALERT_VIEWER
    }