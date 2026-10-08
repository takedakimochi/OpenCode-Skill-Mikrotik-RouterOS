#!/usr/bin/env python3
"""RosAPI - RouterOS binary API (TCP 8728) client for the mikrotik-kios skill.

Thin CLI wrapper around the RouterOS-api library (socialwifi/RouterOS-api):
https://github.com/socialwifi/RouterOS-api

Handles connect + login automatically (MD5 challenge or plaintext secure mode,
depending on RouterOS version), then executes path/command + params.

Settings come from env with defaults matching the owner's kios router:
    ROS_HOST, ROS_PORT, ROS_USER, ROS_PASS

Usage:
  rosapi.py status                          login test + identity/resource
  rosapi.py print  /ip/address [PARAMS...]  list (supports ?filter=value)
  rosapi.py add    /queue/simple PARAMS...  create
  rosapi.py set    /queue/simple PARAMS...  update (needs =.id=*N)
  rosapi.py remove /queue/simple PARAMS...  delete (needs =.id=*N)
  rosapi.py exec   /system/reboot PARAMS... run arbitrary command
"""
from __future__ import annotations

import json
import os
import sys
import traceback

import routeros_api
from routeros_api.exceptions import RouterOsApiCommunicationError

DEFAULT_HOST = "10.10.3.1"
DEFAULT_PORT = 8728
DEFAULT_USER = "sistem"
DEFAULT_PASS = "sistem"


def _host():
    return os.environ.get("ROS_HOST", DEFAULT_HOST)


def _port():
    return int(os.environ.get("ROS_PORT", DEFAULT_PORT))


def _user():
    return os.environ.get("ROS_USER", DEFAULT_USER)


def _pass():
    return os.environ.get("ROS_PASS", DEFAULT_PASS)


class RosError(RuntimeError):
    pass


class RosTrap(RosError):
    def __init__(self, message, category=""):
        super().__init__(message)
        self.message = message
        self.category = category


class RosConnection:
    """Wraps routeros_api.RouterOsApiPool + a logged-in api handle."""

    def __init__(self, host=None, port=None, user=None, password=None):
        self.host = host or _host()
        self.port = port or _port()
        self.user = user or _user()
        self.password = password or _pass()
        self.pool, self.api = self._login()

    def _login(self):
        last = None
        for plaintext in (False, True):
            pool = routeros_api.RouterOsApiPool(
                self.host, username=self.user, password=self.password,
                port=self.port, plaintext_login=plaintext, use_ssl=False)
            try:
                return pool, pool.get_api()
            except Exception as e:  # try the other login flavor
                last = e
                try:
                    pool.disconnect()
                except Exception:
                    pass
        if isinstance(last, RouterOsApiCommunicationError):
            raise RosTrap(_trap_message(last))
        raise RosError(str(last))


def _trap_message(exc):
    msg = getattr(exc, "message", None) or getattr(exc, "original_message", None) \
        or str(exc)
    if isinstance(msg, (tuple, list)):
        msg = msg[0] if msg else ""
    if not isinstance(msg, str):
        msg = msg.decode("utf-8", "replace") if isinstance(msg, bytes) else str(msg)
    msg = msg.replace("Error \"", "").rstrip('"')
    return msg.strip() or str(exc)


def _trap_category(exc):
    return getattr(exc, "category", "")


def _split_params(params):
    query = {}
    args = {}
    for p in params:
        if p.startswith("?") and "=" in p:
            k, _, v = p[1:].partition("=")
            query[k] = v.encode()
        elif p.startswith("="):
            k, _, v = p[1:].partition("=")
            args[k] = v.encode()
        else:
            args[p] = b""
    return args, query


def _s(v):
    if v is None:
        return ""
    return v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)


def _rows(promise):
    return [dict(r) for r in promise]


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    op = argv[1]

    try:
        conn = RosConnection()
        if op == "status":
            ident_rows = _rows(conn.api.get_binary_resource(
                "/system/identity").call("print")) or [{}]
            res = _rows(conn.api.get_binary_resource(
                "/system/resource").call("print")) or [{}]
            ident = ident_rows[0]
            res = res[0]
            print(json.dumps({
                "identity": _s(ident.get("name")),
                "board": _s(res.get("board-name")),
                "version": _s(res.get("version")),
                "cpu": _s(res.get("cpu")),
                "cpu-load": _s(res.get("cpu-load")),
                "uptime": _s(res.get("uptime")),
                "free-memory": _s(res.get("free-memory")),
                "total-memory": _s(res.get("total-memory")),
            }, indent=2, sort_keys=True))
        else:
            path = argv[2]
            args, query = _split_params(argv[3:])
            resource = conn.api.get_binary_resource(path)
            try:
                promise = resource.call(op, arguments=args, queries=query,
                                        additional_queries=())
            except RouterOsApiCommunicationError as e:
                raise RosTrap(_trap_message(e))
            if op == "print":
                print(json.dumps(_rows(promise), indent=2, sort_keys=True,
                                 default=_s))
            elif promise.done_message:
                print(json.dumps(
                    dict((_s(k), _s(v))
                         for k, v in promise.done_message.items()),
                    indent=2, sort_keys=True))
            else:
                print("ok")
        return 0
    except RosTrap as e:
        print("[trap] %s" % e.message, file=sys.stderr)
        return 2
    except Exception as e:
        print("error: %s" % e, file=sys.stderr)
        if os.environ.get("ROS_DEBUG"):
            traceback.print_exc()
        return 3


if __name__ == "__main__":
    sys.exit(main(sys.argv))