import attr
import requests
import pydantic
import httpx
import httpx._types

import enumb

import functools
import typing
import urllib.parse

from pprint import pprint as pp

'''
import flient

app = fastapiclient.FastAPIClient()

@app.get('/ip')
def ip(): pass

httpbin = app.client('https://httpbin.org/)

print(httpbin.ip())
'''

class DataSource(enumb.AutoStrEnum):
    YOUTUBE: str = 'yt'

class Bool(enumb.AutoStrEnum):
    _generate_next_value_ = lambda name, *_: name[0].lower()

    TRUE:  str
    FALSE: str

class Frontend(enumb.AutoNameSlug):
    YOUTUBE:               str
    YOUTUBE_PEGASUS_WEB:   str
    YOUTUBE_MUSIC_ANDROID: str
    YOUTUBE_MUSIC_IOS:     str
    YOUTUBE_LR:            str
    CHROME:                str
    FIREFOX:               str

class Header(enumb.AutoNameSlugTitle):
    CONTENT_LENGTH: str

@attr.s(auto_attribs=True)
class Request(object):
    params:  httpx._types.QueryParamTypes = None
    headers: httpx._types.HeaderTypes     = None
    cookies: httpx._types.CookieTypes     = None
    content: httpx._types.RequestContent  = None
    data:    httpx._types.RequestData     = None
    files:   httpx._types.RequestFiles    = None
    data:    httpx._types.RequestData     = None
    json:    typing.Any                   = None
    method:  typing.Union \
    [
        str,
        bytes,
        None,
    ] = None
    url:     typing.Union \
    [
        httpx.URL,
        str,
        httpx._types.RawURL,
        None,
    ] = None

class FastAPIClient(object):
    def __init__(self):
        self.operations = {}

    def get(self, path: str):
        return self.request('GET', path)

    def request(self, method: str, path: str):
        def decorator(func):
            @pydantic.validate_arguments
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                request = func(*args, **kwargs)

                if request is None:
                    request = Request()

                request.method = method
                request.url    = path

                return request

            self.operations[func.__name__] = wrapper

            return wrapper

        return decorator

    def client(self, base_url: str, **kwargs):
        return Client \
        (
            self,
            httpx.Client \
            (
                base_url = base_url,
                ** kwargs,
            ),
        )

class Client(object):
    def __init__(self, app, session):
        self._app     = app
        self._session = session

        for operation_name, operation in self._app.operations.items():
            def decorator(self, operation):
                @functools.wraps(operation)
                def wrapper(*args, **kwargs):
                    schema = operation(*args, **kwargs)

                    request = self._session.build_request(** attr.asdict(schema))

                    return self._session.send(request)

                return wrapper

            setattr(self, operation_name, decorator(self, operation))

app = FastAPIClient()

@app.get('/complete/search') # , parser=
def complete_search \
        (
            query:       str,
            frontend:    Frontend,
            data_source: typing.Optional[DataSource] = None,
        ) -> Request:
    return Request \
    (
        params = dict \
        (
            q      = query,
            client = frontend,
            xhr    = Bool.TRUE,
            hjson  = Bool.TRUE,
        ),
    )

client = app.client('https://suggestqueries.google.com/')

d = client.complete_search('foo', frontend = Frontend.YOUTUBE)

pp(d.json())
