import enum
import os
from datetime import datetime
from pathlib import Path
from typing import Iterable

import ciso8601
import click
from dateutil import tz


class ItemProvider(enum.Enum):
    PRODUCER = "producer"
    PROCESSOR = "processor"
    HOST = "host"
    LICENSOR = "licensor"


class ClickDatetime(click.ParamType):
    """
    Take a datetime parameter, supporting any ISO8601 date/time/timezone combination.
    """

    name = "date"

    def convert(self, value, param, ctx):
        if value is None:
            return value

        if isinstance(value, datetime):
            return value

        try:
            return ciso8601.parse_datetime(value)
        except ValueError:
            self.fail(
                (
                    "Invalid date string {!r}. Expected any ISO date/time format "
                    '(eg. "2017-04-03" or "2014-05-14 12:34")'.format(value)
                ),
                param,
                ctx,
            )


def read_paths_from_file(listing: Path) -> Iterable[Path]:
    """
    A generator that yields path from a file; paths encoded one per line
    """
    with listing.open("r") as f:
        for loc in f.readlines():
            path = Path(loc.strip())
            if not path.exists():
                raise FileNotFoundError(
                    "No such file or directory: %s" % (os.path.abspath(loc),)
                )

            yield path.absolute()


def default_utc(d: datetime):
    if d.tzinfo is None:
        return d.replace(tzinfo=tz.tzutc())
    return d


def subfolderise(code: str):
    """
    Cut a string folder name into subfolders if long.

    (Forward slashes only, as it assumes you're using Pathlib's normalisation)

    >>> subfolderise('089090')
    '089/090'
    >>> # Prefer fewer folders in first level.
    >>> subfolderise('12345')
    '12/345'
    >>> subfolderise('123456')
    '123/456'
    >>> subfolderise('1234567')
    '123/4567'
    >>> subfolderise('12')
    '12'
    """
    if len(code) > 2:
        return "/".join((code[: len(code) // 2], code[len(code) // 2 :]))
    return code
