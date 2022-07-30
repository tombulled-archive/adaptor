import adaptor
from adaptor import sessions, adaptors
from pprint import pprint as pp
import functools
import attr

# s = sessions.BaseUrlSession(base_url = 'https://httpbin.org/')
# s = sessions.BaseUrlSession(base_url = 'https://suggestqueries.google.com/')
# a = adaptors.Adaptor(session = s)

@attr.s
class SuggestQueriesSession(sessions.BaseUrlSession):
    base_url: str = 'https://suggestqueries.google.com/'

@attr.s
class SuggestQueriesAdaptor(adaptors.Adaptor):
    session: SuggestQueriesSession = attr.ib \
    (
        default = SuggestQueriesSession,
    )

@attr.s
class SuggestQueries(object):
    adaptor: SuggestQueriesAdaptor = attr.ib \
    (
        default = SuggestQueriesAdaptor,
    )

    def complete_search(self, **kwargs):
        return self.adaptor.get('complete/search', **kwargs)

sq = SuggestQueries()

# r = sq.complete_search \
# (
#     params = dict \
#     (
#         client = 'youtube',
#         q      = 'foo',
#         ds     = 'yt',
#         xhr    = 't',
#         hjson  = 't',
#     ),
# )
#
# pp(r.json())

# class MyApiClient:
#     @foo.get('/item/{id}')
#     def get_item(self, id: int):
#         ...
#
#     @api.get('complete/search')
#     def complete_search(self, client: )
