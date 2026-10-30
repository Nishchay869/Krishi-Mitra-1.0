"""Compatibility entry point: Disease Check now uses Gemini, never the local CNN."""
from .gemini import DiagnosisError as ModelNotTrained, analyze_leaf as predict

__all__ = ['ModelNotTrained', 'predict']
