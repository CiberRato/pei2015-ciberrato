from django.core.validators import RegexValidator
import re

slug_re = re.compile(r'^[-a-zA-Z0-9_ ]+$')
validate_word = RegexValidator(slug_re, "Enter a valid word consisting of letters, numbers, underscores, spaces or hyphens.", 'invalid')
