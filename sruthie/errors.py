class SruthieError(Exception):
    """
    General sruthie error class to provide a superclass for all other errors
    """

class ServerIncompatibleError(SruthieError):
    """
    The error raised from sru.search/sru.explain when the server doesn't behave
    like a SRU endpoint.
    """