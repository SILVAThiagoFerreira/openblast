"""Excecoes especificas do pipeline."""


class PipelineError(Exception):
    """Classe base para falhas do sistema."""


class ConfigError(PipelineError):
    """Falha na leitura ou validacao da configuracao."""


class InputDataError(PipelineError):
    """Falha na leitura estrutural da planilha."""


class ValidationError(PipelineError):
    """Falha de validacao semantica ou operacional."""


class ProcessingError(PipelineError):
    """Falha durante o enriquecimento ou montagem do manifesto."""


class OutputError(PipelineError):
    """Falha na escrita dos artefatos de saida."""
