import attr
import requests

import urllib.parse
import typing

@attr.s
class BaseSession(requests.Session):
    def __attrs_pre_init__(self):
        super().__init__()

@attr.s
class BaseUrlSession(BaseSession):
    base_url: typing.Optional[str] = attr.ib \
    (
        default = None,
    )

    def prepare_request(self, request: requests.Request) -> requests.PreparedRequest:
        if self.base_url is not None:
            request.url = urllib.parse.urljoin(self.base_url, request.url)

        return super().prepare_request(request)
