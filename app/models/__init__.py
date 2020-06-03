from abc import ABC, abstractmethod
from collections.abc import Sequence

from flask import abort


class JSONModel():

    ALLOWED_PROPERTIES = set()

    def __init__(self, _dict):
        # in the case of a bad request _dict may be `None`
        self._dict = _dict or {}

    def __bool__(self):
        return self._dict != {}

    def __hash__(self):
        return hash(self.id)

    def __dir__(self):
        return super().__dir__() + list(sorted(self.ALLOWED_PROPERTIES))

    def __eq__(self, other):
        return self.id == other.id

    def __getattribute__(self, attr):

        try:
            return super().__getattribute__(attr)
        except AttributeError as e:
            # Re-raise any `AttributeError`s that are not directly on
            # this object because they indicate an underlying exception
            # that we don’t want to swallow
            if str(e) != "'{}' object has no attribute '{}'".format(
                self.__class__.__name__, attr
            ):
                raise e

        if attr in super().__getattribute__('ALLOWED_PROPERTIES'):
            return super().__getattribute__('_dict')[attr]

        raise AttributeError((
            "'{}' object has no attribute '{}' and '{}' is not a field "
            "in the underlying JSON"
        ).format(
            self.__class__.__name__, attr, attr
        ))

    def _get_by_id(self, things, id):
        try:
            return next(thing for thing in things if thing['id'] == str(id))
        except StopIteration:
            abort(404)


class ModelList(ABC, Sequence):

    @property
    @abstractmethod
    def client_method(self):
        pass

    @property
    @abstractmethod
    def model(self):
        pass

    def __init__(self, *args, **kwargs):
        self.items = self.client_method(*args, **kwargs)

    def __getitem__(self, index):
        return self.model(self.items[index])

    def __len__(self):
        return len(self.items)

    def __add__(self, other):
        return list(self) + list(other)

    def __radd__(self, other):
        return list(other) + list(self)


class PaginatedModelList(ModelList):

    response_key = 'data'

    def __init__(self, *args, page=None, **kwargs):
        try:
            self.current_page = int(page)
        except TypeError:
            self.current_page = 1
        response = self.client_method(
            *args,
            **kwargs,
            page=self.current_page,
        )
        self.items = response[self.response_key]
        self.prev_page = response.get('links', {}).get('prev', None)
        self.next_page = response.get('links', {}).get('next', None)
