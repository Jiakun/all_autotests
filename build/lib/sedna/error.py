""" module contains error definitions """


class NoneReferenceError(ValueError):
    """Error indicates that a None is given unexpectedly"""

    def __init__(self, *args, **kwargs):
        super(NoneReferenceError, self).__init__(args, kwargs)


class IllegalStateError(AttributeError):
    """
    Error indicates that the state is not legal for the consequential process
    """

    def __init__(self, *args, **kwargs):
        super(IllegalStateError, self).__init__(args, kwargs)
