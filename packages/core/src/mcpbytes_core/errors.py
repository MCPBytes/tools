class ToolError(Exception):
    """A failure the user can act on: a stable code (the hosted API's codes where they exist), a message, a hint."""

    def __init__(self, code, message, hint=None):
        self.code, self.hint = code, hint
        super().__init__(message)

    def __str__(self):
        return f"{self.code}: {self.args[0]}" + (f" ({self.hint})" if self.hint else "")
