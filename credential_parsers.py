class BaseParser:
    """Base class for parsing credentials files."""

    @staticmethod
    def parse(credential, *args):
        return credential.strip('\n')
