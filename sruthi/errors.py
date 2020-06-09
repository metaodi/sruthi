class SruthiError(Exception):
    """
    General sruthi error class to provide a superclass for all other errors
    """


class ServerIncompatibleError(SruthiError):
    """
    The error raised from sru.search/sru.explain when the server doesn't behave
    like a SRU endpoint.
    """


class SruError(SruthiError):
    """
    The error raised from sru.search/sru.explain when the SRU response contains
    an error
    """


class NoMoreRecordsError(SruthiError):
    """
    This error is raised if all records have been loaded (or no records are
    present)
    """


class SruthiWarning(Warning):
    """
    General sruthi warning class to provide a superclass for all warnings
    """


class WrongNamespaceWarning(SruthiWarning):
    """
    A warning to indicate, that a server uses the wrong SRU namespace.
    """
