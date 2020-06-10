__version__ = '0.0.1'
__all__ = ['errors', 'sru', 'client']

from sruthi.errors import SruthiError, ServerIncompatibleError, SruError, NoMoreRecordsError
from sruthi.errors import SruthiWarning, WrongNamespaceWarning
from sruthi.sru import searchretrieve, explain
from sruthi.client import Client
