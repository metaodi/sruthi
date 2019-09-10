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
    The error raised from sru.search/sru.explain when the SRU response contains an error
    """
