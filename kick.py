import re
import logging
import webview
import json
from streamlink.plugin import Plugin, pluginmatcher
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream
from streamlink.exceptions import PluginError

log = logging.getLogger(__name__)

@pluginmatcher(
    re.compile(
        r"https?://(?:www\.)?kick\.com/(?!(?:video|categories|search|auth)(?:[/?#]|$))(?P<channel>[\w_-]+)$",
    ),
    name="live",
)
@pluginmatcher(
    re.compile(
        r"https?://(?:www\.)?kick\.com/video/(?P<video_id>[\da-f]{8}-(?:[\da-f]{4}-){3}[\da-f]{12})",
    ),
    name="vod",
)
@pluginmatcher(
    re.compile(
        r"https?://(?:www\.)?kick\.com/(?!(?:video|categories|search|auth)(?:[/?#]|$))(?P<channel>[\w_-]+)\?clip=(?P<clip_id>[\w_]+)$",
    ),
    name="clip",
)
class KICK(Plugin):
    def _get_streams(self):
        API_BASE_URL = "https://kick.com/api"

        _LIVE_SCHEMA = validate.Schema(
            validate.parse_json(),
            {
                "playback_url": validate.url(path=validate.endswith(".m3u8")),
                "livestream": {
                    "is_live": True,
                    "id": int,
                    "session_title": str,
                    "categories": [{"name": str}],
                },
                "user": {"username": str},
            },
            validate.union_get(
                "playback_url",
                ("livestream", "id"),
                ("user", "username"),
                ("livestream", "session_title"),
                ("livestream", "categories", 0, "name"),
            ),
        )

        _VIDEO_SCHEMA = validate.Schema(
            validate.parse_json(),
            {
                "source": validate.url(path=validate.endswith(".m3u8")),
                "id": int,
                "livestream": {
                    "channel": {"user": {"username": str}},
                    "session_title": str,
                    "categories": [{"name": str}],
                },
            },
            validate.union_get(
                "source",
                "id",
                ("livestream", "channel", "user", "username"),
                ("livestream", "session_title"),
                ("livestream", "categories", 0, "name"),
            ),
        )

        _CLIP_SCHEMA = validate.Schema(
            validate.parse_json(),
            {
                "clip": {
                    "video_url": validate.url(path=validate.endswith(".m3u8")),
                    "id": str,
                    "channel": {"username": str},
                    "title": str,
                    "category": {"name": str},
                },
            },
            validate.union_get(
                ("clip", "video_url"),
                ("clip", "id"),
                ("clip", "channel", "username"),
                ("clip", "title"),
                ("clip", "category", "name"),
            ),
        )

        live, vod, clip = (
            self.matches["live"],
            self.matches["vod"],
            self.matches["clip"],
        )

        api_url = "{0}/{1}/{2}".format(
            API_BASE_URL,
            *(
                ["v1/channels", self.match["channel"]]
                if live
                else (
                    ["v1/video", self.match["video_id"]]
                    if vod
                    else ["v2/clips", self.match["clip_id"]]
                )
            )
        )

        class ApiHandler:
            def __init__(self):
                self.page_content = None
                self.win = None

            def set_win(self, window):
                self.win = window
                

            def get_content(self):
                try:
                    self.page_content = self.win.evaluate_js("document.body.innerText")
                    json.loads(self.page_content)
                except Exception as e:
                    return False

                self.win.destroy()    
                
        handler = ApiHandler()

        window = webview.create_window('Kick API Request', api_url, width=800, height=600)
        window.events.loaded += handler.get_content

        webview.start(handler.set_win, window, gui='edgechromium')  # Log the beginning of the content

        try:
            url, self.id, self.author, self.title, self.category = (
                _LIVE_SCHEMA if live else (_VIDEO_SCHEMA if vod else _CLIP_SCHEMA)
            ).validate(handler.page_content)
        except (PluginError, TypeError) as err:
            log.debug(err)
            return

   
        if live or vod:
            yield from HLSStream.parse_variant_playlist(self.session, url).items()
        elif (
            clip and self.author.casefold() == self.match["channel"].casefold()
        ):  # Sanity check if the clip channel is the same as the one in the URL
            yield "source", HLSStream(self.session, url)

__plugin__ = KICK
