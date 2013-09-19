from django.utils.html import strip_tags
import re

def get_excerpt(description, size=140):
    """
    Creates an excerpt of an object description.
    Returns the first sentence, or first line,
    or a fixed size prefix (whichever is shortest).
    """
    description = strip_tags(description)
    match = re.search("\.|\\r|\\n", description)
    position = size
    if match:
        start = match.start()
        if start < position:
            position = start
    return description[:position]
