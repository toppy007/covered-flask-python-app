from markupsafe import Markup

def nl2br(value):
    if value is None:
        return ""
    return Markup(value.replace('\n', '<br>'))