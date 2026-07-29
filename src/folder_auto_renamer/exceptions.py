"""Custom exception classes for folder-auto-renamer."""


class FolderAutoRenamerError(Exception):
    """Base exception class for all errors in folder-auto-renamer."""
    pass


class DirectoryNotFoundError(FolderAutoRenamerError):
    """Raised when the specified target directory does not exist."""
    pass


class NotADirectoryError(FolderAutoRenamerError):
    """Raised when the specified target path is a file rather than a directory."""
    pass


class PermissionDeniedError(FolderAutoRenamerError):
    """Raised when permission is denied while accessing or renaming a folder."""
    pass


class FolderAlreadyExistsError(FolderAutoRenamerError):
    """Raised when the target folder name already exists during rename operations."""
    pass


class UndoError(FolderAutoRenamerError):
    """Raised when undoing a rename operation fails or no history is found."""
    pass


class ConfigurationError(FolderAutoRenamerError):
    """Raised when invalid command-line configuration arguments are provided."""
    pass
