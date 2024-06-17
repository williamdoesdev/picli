class PICLIConfigError(Exception):
    def __init__(self, message):
        super().__init__(message)
    
class PICLICommandError(Exception):
    def __init__(self, message):
        super().__init__(message)
    
class PICLIInitError(Exception):
    def __init__(self, message):
        super().__init__(message)

class PICLIShutdownError(Exception):
    def __init__(self, message):
        super().__init__(message)

class PICLIValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)

class PICLIWebAPIError(Exception):
    def __init__(self, message):
        super().__init__(message)