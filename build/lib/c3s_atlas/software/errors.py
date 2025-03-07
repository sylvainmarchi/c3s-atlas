class ConfigurationFileWrongDefinition(Exception):
    """Raise an error when the configuration file is not defined properly."""

    def __init__(self, message):
        self.message = message


class RequestFailedError(Exception):
    """Raise an error when commons request fails."""

    def __init__(self, message):
        self.message = message


class InferFrequencyError(Exception):
    """Raise an error when unable to infer the frequency of the dataset."""

    def __init__(self, message):
        self.message = message


class ConcatError(Exception):
    """Raise an error when unable to concat the datasets by dimension time."""

    def __init__(self, message):
        self.message = message


class NotClimateIndexDefined(Exception):
    """Raise an error when commons requested ClimateIndex is not defined in the code."""

    def __init__(self, message):
        self.message = message


class NoDataFound(Exception):
    """Raise an error when not data is found inside the Output class."""

    def __init__(self, message):
        self.message = message


class NotIcclimIndexImplementation(Exception):
    """Raise an error when not icclim implementation."""

    def __init__(self, message):
        self.message = message
