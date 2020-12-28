from pymongo.errors import (
    ConfigurationError,
    ConnectionFailure,
    WriteConcernError,
)


class MongoError:
    ConfigurationError = ConfigurationError
    ConnectionFailure = ConnectionFailure
    WriteConcernError = WriteConcernError

    err_text_map = {
        ""
    }

