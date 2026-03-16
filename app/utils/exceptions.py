class AppException(Exception):
    def __init__(self,  status_code: int = 400, message: str="Something went wrong!"):
        self.status_code = status_code
        self.message = message