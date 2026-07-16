from __future__ import annotations


class ProjectError(Exception):
    """Base class for all project-specific failures."""


class ConfigurationError(ProjectError):
    """Raised when the configuration file is missing or invalid."""


class ValidationError(ProjectError):
    """Raised when input data or processed results fail validation."""


class ProcessingError(ProjectError):
    """Raised when the campaign cannot be processed safely."""


class OutputError(ProjectError):
    """Raised when an output artifact cannot be created or verified."""
