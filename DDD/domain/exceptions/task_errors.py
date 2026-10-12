"""Domain failures raised when task invariants are violated."""


class InvalidTask(ValueError):
    """A task value violates a business invariant."""


class InvalidUserId(ValueError):
    """A user identity cannot safely own domain data."""
