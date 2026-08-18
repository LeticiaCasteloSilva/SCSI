import re

from django.core.exceptions import ValidationError

CNPJ_DIGITS = 14
CNPJ_FIRST_WEIGHTS = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
CNPJ_SECOND_WEIGHTS = [6] + CNPJ_FIRST_WEIGHTS


def strip_non_digits(value):
    return re.sub(r'\D', '', value or '')


def _check_digit(digits, weights):
    total = sum(int(digit) * weight for digit, weight in zip(digits, weights))
    remainder = total % 11
    return 0 if remainder < 2 else 11 - remainder


def validate_cnpj(value):
    """Validate a CNPJ by its two check digits, ignoring any mask."""
    digits = strip_non_digits(value)

    if len(digits) != CNPJ_DIGITS:
        raise ValidationError('O CNPJ deve conter 14 dígitos.', code='cnpj_length')

    if digits == digits[0] * CNPJ_DIGITS:
        raise ValidationError('CNPJ inválido.', code='cnpj_repeated')

    first = _check_digit(digits[:12], CNPJ_FIRST_WEIGHTS)
    second = _check_digit(digits[:13], CNPJ_SECOND_WEIGHTS)

    if digits[12] != str(first) or digits[13] != str(second):
        raise ValidationError('CNPJ inválido.', code='cnpj_invalid')


def format_cnpj(value):
    """Return the CNPJ in the masked form `XX.XXX.XXX/XXXX-XX`.

    Normalising on save keeps the uniqueness constraint meaningful: the same
    company typed with and without the mask must collide.
    """
    digits = strip_non_digits(value)
    if len(digits) != CNPJ_DIGITS:
        return value
    return f'{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}'
