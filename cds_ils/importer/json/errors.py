from invenio_rest.errors import RESTException


class ImporterException(RESTException):
    """Importer exception."""

    code = 400

    def __init__(self, errors=None, description=None, **kwargs):
        self.description = description
        super().__init__(errors, **kwargs)
