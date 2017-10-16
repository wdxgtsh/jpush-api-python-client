import re
import sys

# Valid autobadge values: auto, +N, -N
VALID_AUTOBADGE = re.compile(r'^(auto|[+-][\d]+)$')


PY2 = sys.version_info[0] == 2

if not PY2:
    string_types = (str,)
else:
    string_types = (str, unicode)


def notification(alert=None, ios=None, android=None, winphone=None):
    """Create a notification payload.

    :keyword alert: A simple text alert, applicable for all platforms.
    :keyword ios: An iOS platform override, as generated by :py:func:`ios`.
    :keyword android: An Android platform override, as generated by :py:func:`android`.
    :keyword winphone: A MPNS platform override, as generated by :py:func:`mpns`.

    """
    payload = {}
    if alert is not None:
        payload['alert'] = alert
    if ios is not None:
        payload['ios'] = ios
    if android is not None:
        payload['android'] = android
    if winphone is not None:
        payload['winphone'] = winphone
    if not payload:
        raise ValueError("Notification body may not be empty")
    return payload


def ios(alert=None, badge='+1', sound=None, content_available=False,
    mutable_content=False, category=None, extras=None, sound_disable=False):
    """iOS/APNS specific platform override payload.

    :keyword alert: iOS format alert, as either a string or dictionary.
    :keyword badge: An integer badge value or an *autobadge* string.
    :keyword sound: An string sound file to play.
    :keyword content_available: If True, pass on the content-available command
        for Newsstand iOS applications.
    :keyword extra: A set of key/value pairs to include in the push payload
        sent to the device.
    :keyword sound_disalbe: Disable sound to implement slient push.

    >>> ios(alert='Hello!', sound='cat.caf',
    ...     extra={'articleid': '12345'})
    {'sound': 'cat.caf', 'extra': {'articleid': '12345'}, 'alert': 'Hello!'}

    """
    payload = {}
    if alert is not None:
        if not isinstance(alert, (string_types, dict)):
            raise ValueError("iOS alert must be a string or dictionary")
        payload['alert'] = alert
    if badge is not None:
        if not (isinstance(badge, str) or isinstance(badge, int)):
            raise ValueError("iOS badge must be an integer or string")
        if isinstance(badge, str) and not VALID_AUTOBADGE.match(badge):
            raise ValueError("Invalid iOS autobadge value")
        payload['badge'] = badge
    if not sound_disable:
        if sound is not None:
            payload['sound'] = sound
        else:
            payload['sound'] = 'default'
    if content_available:
        payload['content-available'] = 1
    if mutable_content:
        payload['mutable-content'] = 1
    if category:
        payload['category'] = category
    if extras is not None:
        payload['extras'] = extras
    return payload

def android(alert, title=None, builder_id=None, extras=None,
        priority=None, category=None, style=None,
        alert_type=None,big_text=None, inbox=None, big_pic_path=None,
        uri_activity=None):
    """Android specific platform override payload.

    :keyword alert: String alert text.If you set alert to a empty string,then the payload
    will not display on notification bar.
    more info:https://docs.jiguang.cn/jpush/server/push/rest_api_v3_push/#notification
    :keyword alert: String alert text.
    :keyword title: String
    :keyword builder_id: Integer
    :keyword extras: A set of key/value pairs to include in the push payload
        sent to the device.
    """
    payload = {}
    if alert is not None:
        payload['alert'] = alert
    if title is not None:
        payload['title'] = title
    if builder_id is not None:
        payload['builder_id'] = builder_id
    if priority is not None:
        payload['priority'] = priority
    if category is not None:
        payload['category'] = category
    if style is not None:
        payload['style'] = style
    if alert_type is not None:
        payload['alert_type'] = alert_type
    if big_text is not None:
        payload['big_text'] = big_text
    if inbox is not None:
        payload['inbox'] = inbox
    if big_pic_path is not None:
        payload['big_pic_path'] = big_pic_path
    if uri_activity is not None:
        payload['uri_activity'] = uri_activity
    if extras is not None:
        payload['extras'] = extras
    return payload


def winphone(alert, title=None, _open_page=None, extras=None):
    """MPNS specific platform override payload.

    Must include exactly one of ``alert``, ``title``, ``_open_page``, or ``extras``.

    """
    if len(list(filter(None, (alert, _open_page, title)))) != 1:
        raise ValueError("MPNS payload must have one notification type.")
    payload = {}
    if alert is not None:
        payload['alert'] = alert
    if title is not None:
        payload['title'] = title
    if _open_page is not None:
        payload['_open_page'] = _open_page
    if extras is not None:
        payload['extras'] = extras
    return payload

def message(msg_content, title=None, content_type=None, extras=None):
    """Inner-conn push message payload creation.

    :param msg_content: Required, string
    :param title: Optional, string
    :keyword content_type: Optional, MIME type of the body
    :keyword extras: Optional, dictionary of string values.

    """
    payload = {
        'msg_content': msg_content,
    }
    if title is not None:
        payload['title'] = title
    if content_type is not None:
        payload['content_type'] = content_type
    if extras is not None:
        payload['extras'] = extras
    return payload


def smsmessage(content,delay_time):
    payload = {}
    payload["content"]=content
    payload["delay_time"]=delay_time
    return payload


def cid(cid):
    payload = {}
    payload["cid"]=cid
    return payload

def platform(*types):
    """Create a platform specifier.

    >>> platform('ios', 'winphone')
    ['ios', 'winphone']
    >>> platform('ios', 'symbian')
    Traceback (most recent call last):
        ...
    ValueError: Invalid platform 'symbian'

    """
    if len(types) == 1 and types[0] == 'all':
        return 'all'
    for t in types:
        if t not in ('ios', 'android', 'winphone'):
            raise ValueError("Invalid platform '%s'" % t)
    return [t for t in types]

def options(options):
    """Create options object."""
    return {"options": options}

def audience(*types):
    """Select audience that match all of the given selectors.

    >>> audience(tag('sports'), tag_and('business'))
    {'audience': {'tag':['sports'], 'tag_and':['business']}}

    """
    if 1 == len(types) and 'all' == types[0]:
        return "all"
    audience = {}
    for t in types:
        for key in t:
            if key not in ('tag', 'tag_and', 'tag_not', 'alias', 'registration_id', 'segment', 'abtest'):
                raise ValueError("Invalid audience '%s'" % t)
            audience[key] = t[key]
    return audience
