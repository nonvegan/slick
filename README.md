# Streamlink Kick plugin

A Simple [Kick.com](https://kick.com) plugin for [Streamlink](https://github.com/streamlink/streamlink). This plugin uses an extra dependency [webview](https://github.com/r0x0r/pywebview) in order to try to access KICK's Cloudflare protected public API, until KICK provides a more streamlined way to do so.

## Install
* pip install [pywebview](https://pypi.org/project/pywebview/)
  * For Windows users with Streamlink builds which come bundled with an embedded Python environment, regular pip will not suffice and a ModuleNotFoundError will be raised when running Streamlink. You can fix this by adding `--target=<StreamLinkInstallPath>\pkgs`
* Copy the [kick.py](kick.py) file into one of the [sideload directories](https://streamlink.github.io/cli/plugin-sideloading.html)


## Usage
```
streamlink kick.com/trainwreckstv best
streamlink kick.com/video/c32a463d-4f4e-44f8-a5f3-88e8c5c8e720 best
streamlink kick.com/trainwreckstv?clip=clip_01H6V5QHN7VMYHKNYVY7B6FRWW best
```

---
**TIP**

You can passthrough the stream feed to your player using the [```--player-passthrough TYPES```](https://streamlink.github.io/cli.html#cmdoption-player-passthrough) option

---


