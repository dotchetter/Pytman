from queue import Queue, Empty
import collections
import os
import re
from datetime import datetime
from typing import List, Iterable


class MessageMixin:
    """
    Pyttman MessageMixin, to extend the functionalty
    of existing Message classes provided by 3rd party
    libraries and APIs, to also accommodate for the
    internal requirements of the Message object
    which is expected to fulfill a certain contract
    of attributes and methods for parsing messages.

    The MessageMixin class can be included in multiple
    inheritance when a Message-like class is developed
    for supporting a 3rd party library / API.
    """

    def __init__(self, content=None, **kwargs):
        self.author = "anonymous"
        self.created = datetime.now()
        self.client = None
        self.content = content

        try:
            self.content_with_format = str(content).splitlines(keepends=True)
        except ValueError:
            self.content_with_format = None

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return f"{self.__class__.__name__}(author=" \
               f"{self.author}, created={self.created}, " \
               f"content={self.content})"

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, val):
        if val is None:
            self._content = ["None"]
        elif isinstance(val, str):
            self._content = val.split()
        elif isinstance(val, list) or isinstance(val, tuple):
            self._content = [str(i) for i in val]
        elif isinstance(val, dict):
            self._content = str(val).split()
        else:
            try:
                self._content = repr(val).split()
            except Exception:
                raise TypeError(f"content cannot be type {type(val)} "
                                f"as it is could not be typecasted to "
                                f"str.")

    def sanitized_content(self, preserve_case=False) -> List[str]:
        """
        Return a sanitized version of the .content property.
        This means that the contents in the message
        are stripped of all symbols while case and
        digits are still kept.
        :return: list
        """
        out = []
        for i in self.content:
            sanitized = re.sub(r"[^\w\s]", "", i)
            if preserve_case:
                out.append(sanitized)
            else:
                out.append(sanitized.lower())
        return out

    def lowered_content(self) -> List[str]:
        """
        Returns the content of the message case lowered.
        :return: list, str
        """
        return [i.lower() for i in self.content]

    def as_str(self, sanitized: bool = False) -> str:
        """
        Return the 'content' field as joined string
        :param sanitized: Return the content as sanitized_content or not
        :return: str
        """
        if sanitized:
            return " ".join(self.sanitized_content())
        elif self.content_with_format is not None:
            return str().join(self.content_with_format)
        return " ".join(self.content)

    def as_list(self, sanitized: bool = False) -> List:
        """
        Return the 'content' field as list
        :return: list
        """
        if sanitized:
            content = self.sanitized_content()
        else:
            content = self.content

        if isinstance(content, list):
            return content
        elif isinstance(content, str):
            return content.split()


class Message(MessageMixin):
    """
    Standard implementation of the MessageMixin
    class without extending any functionality.
    """
    pass


class Reply(MessageMixin):
    """
    The Reply object is expected to be  returned
    from all Command subclasses.
    """
    pass


class ReplyStream(Queue):
    """
    The ReplyStream class offers a simple
    interface for app developers to return a
    collection of Reply objects in their app.
    Each item put in a ReplyStream will be
    sent as an individual Reply object.

    It's useful for situations where the response
    for the app can be a collection of items,
    where platforms have message length restrictions
    or are otherwise cumbersome to format as one
    single big Reply. The ReplyStream subclasses
    SimpleQueue and is therefore FIFO.
    """

    def __init__(self, collection: Iterable = None):
        super().__init__()
        if collection is not None:
            map(self._put, collection)

    def get(self, block=True, timeout=None):
        """
        Remove and return an item from the ReplyStream.
        """
        element = self._get()
        return Reply(element) if not isinstance(element, Reply) else element
