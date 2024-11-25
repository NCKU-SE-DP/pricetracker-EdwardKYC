class DomainMismatchException(Exception):
    """
    Raised when the given URL does not belong to the expected domain or its child URLs.
    """

    def __init__(self, url: str):
        super().__init__(f"The URL {url} does not match the expected domain.")
