from typing import Optional, List, Any

MISSING_DEPENDENCY_MESSAGE = """{converter} recognized the input as a potential {extension} file, but the dependencies needed to read {extension} files have not been installed. To resolve this error, include the optional dependency [{feature}] or [all] when installing MarkItUp. For example:

* pip install markitup[{feature}]
* pip install markitup[all]
* pip install markitup[{feature}, ...]
* etc."""


class MissingDependencyException(Exception):
    """
    Converters shipped with MarkItUp may depend on optional
    dependencies. This exception is thrown when a converter's
    convert() method is called, but the required dependency is not
    installed. This is not necessarily a fatal error, as the converter
    will simply be skipped (an error will bubble up only if no other
    suitable converter is found).

    Error messages should clearly indicate which dependency is missing.
    """

    pass


class UnsupportedFormatException(Exception):
    """
    Thrown when no suitable converter was found for the given file.
    """

    pass


class FailedConversionAttempt(Exception):
    """
    Represents a single attempt to convert a file.
    """

    def __init__(self):
        super().__init__(f"Conversion attempt failed!")


class FileConversionException(Exception):
    """
    Thrown when a suitable converter was found, but the conversion
    process fails for any reason.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        attempts: Optional[List[FailedConversionAttempt]] = None,
    ):
        self.attempts = attempts

        if message is None:
            if attempts is None:
                message = "File conversion failed."
            else:
                message = f"File conversion failed after {len(attempts)} attempts:\n"
                for attempt in attempts:
                    if attempt.exc_info is None:
                        message += f" -  {type(attempt.converter).__name__} provided no execution info."
                    else:
                        message += f" - {type(attempt.converter).__name__} threw {attempt.exc_info[0].__name__} with message: {attempt.exc_info[1]}\n"

        super().__init__(message)
