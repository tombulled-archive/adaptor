import attr
import requests

import abc
import functools

from . import sessions

@attr.s
class Adaptor(object):
    session: sessions.BaseSession = attr.ib \
    (
        default = attr.Factory(sessions.BaseSession),
    )

    def __call__ \
            (
                self,
                method: str,
                url:    str,
                params          = None,
                data            = None,
                headers         = None,
                cookies         = None,
                files           = None,
                auth            = None,
                timeout         = None,
                allow_redirects = True,
                proxies         = None,
                hooks           = None,
                stream          = None,
                verify          = None,
                cert            = None,
                json            = None,
            ):
        request = self.request \
        (
            requests.Request \
            (
                method  = method.upper(),
                url     = url,
                headers = headers,
                files   = files,
                data    = data or {},
                json    = json,
                params  = params or {},
                auth    = auth,
                cookies = cookies,
                hooks   = hooks,
            ),
        )

        prepared_request = self.session.prepare_request(request)

        proxies = proxies or {}

        settings = self.session.merge_environment_settings \
        (
            prepared_request.url,
            proxies,
            stream,
            verify,
            cert,
        )

        kwargs = \
        {
            ** dict \
            (
                timeout         = timeout,
                allow_redirects = allow_redirects,
            ),
            ** settings,
        }

        return self.respond(self.session.send(prepared_request, **kwargs))

    def __getattribute__(self, attribute: str):
        try:
            return super().__getattribute__(attribute)
        except AttributeError:
            return functools.partial \
            (
                self,
                attribute.upper(),
            )

    def request(self, request: requests.Request):
        return request

    def respond(self, response: requests.Response):
        return response
