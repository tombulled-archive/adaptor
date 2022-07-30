import fastapi
import fastapi.responses
import fastapi.testclient
import pydantic
import functools
import attr
import requests
import addict
from starlette.types import Receive, Scope, Send
from pprint import pprint as pp
import httpx

import urllib.parse
import typing

import enumb

'''
TODO:
    * Raise exception if error
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

class Request(fastapi.responses.JSONResponse):
    request: httpx.Request

    def __init__(self, content: httpx.Request, **kwargs):
        super().__init__(None)

        self.request = content

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        response = await session.send(self.request)

        self.body = self.render(response.json())

        self.headers[Header.CONTENT_LENGTH] = str(len(self.body))

        await super().__call__(scope, receive, send)

class App(fastapi.FastAPI):
    def __init__(self):
        super().__init__ \
        (
            default_response_class         = Request,
            openapi_url                    = None,
            docs_url                       = None,
            redoc_url                      = None,
            swagger_ui_oauth2_redirect_url = None,
        )

app = App()

@app.on_event('startup')
async def startup_event():
    global session

    session = httpx.AsyncClient \
    (
        base_url = 'https://suggestqueries.google.com/',
    )

@app.on_event('shutdown')
async def shutdown_event():
    await session.aclose()

def decorate(method, path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return Request \
            (
                content = session.build_request \
                (
                    method,
                    path,
                    ** func(*args, **kwargs),
                ),
            )

        return wrapper

    return decorator

@app.get('/complete/search')
@decorate('GET', '/complete/search')
def complete_search \
        (
            query:       str,
            frontend:    Frontend,
            data_source: typing.Optional[DataSource] = None,
        ) -> dict:
    return dict \
    (
        params = dict \
        (
            q      = query,
            client = frontend,
            xhr    = Bool.TRUE,
            hjson  = Bool.TRUE,
            ** (dict(ds = data_source) if data_source is not None else {}),
        ),
    )

class Client(fastapi.testclient.TestClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__enter__()

    def __del__(self):
        self.__exit__()

class Api(object):
    def __init__(self, app):
        self.client = Client(app)

        for route in app.routes:
            def decorator(self, route):
                @functools.wraps(route.endpoint)
                def wrapper(**kwargs):
                    response = self.client.request \
                    (
                        method = next(iter(route.methods)),
                        url    = route.path,
                        params = kwargs,
                    )

                    response.raise_for_status()

                    return response

                return wrapper

            setattr(self, route.name, decorator(self, route))

c = Client(app)
a = Api(app)

d = a.complete_search(query='foo', frontend='chrome').json()
# d = c.get('/complete/search', params=dict(q='foo', client='chrome')).json()

pp(d)

'''
def raise_on_4xx_5xx(response):
    response.raise_for_status()

client = httpx.Client(event_hooks={'response': [raise_on_4xx_5xx]})
'''
