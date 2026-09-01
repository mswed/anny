class AnnyError(Exception):
    """
    Base class for all Anny exceptions
    """


class NoSourceError(AnnyError):
    """
    Raise if we need a source but can't find one
    """
