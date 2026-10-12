"""Application-level failures raised by task use cases."""


class TaskNotFound(Exception):
    """The requested task could not be found by this use case."""
