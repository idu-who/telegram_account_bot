class BaseParser:
    @staticmethod
    def parse(credential, *args):
        return credential.strip('\n')
