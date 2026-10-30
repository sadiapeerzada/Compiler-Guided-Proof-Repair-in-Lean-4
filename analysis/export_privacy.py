"""Distinguish literal privacy-regex syntax from actual exported home paths."""
import re
from .common import private_text


def private_export_text(text):
    # Source guards contain regex alternatives/classes, not actual home names.
    inspected=re.sub(r'/(?:Users|home)/(?=[|)\[(])','[HOME_REGEX_PREFIX]',text)
    inspected=inspected.replace('REDACTED_IDENTITY','[ANONYMOUS_SOURCE_MARKER]')
    return private_text(inspected)
