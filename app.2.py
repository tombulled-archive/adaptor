import pydantic

import typing

'''
api = SomeAPI()

@api.get('complete/search')
def complete_search()
'''

class CompletedSearch(pydantic.BaseModel):
    ...

api = SomeAPI()

@api.get('complete/search')
def complete_search(query: str) -> CompletedSearch:
    return Request \
    (
        params = dict \
        (
            q = query,
        ),
    )
