from django.core.exceptions import ValidationError


def validate_phone_no(phone_no):
    if phone_no[0:2] != '09':
        raise ValidationError('The phone number starts whit 09')
    else:
        return phone_no


def validate_length_phone_no(phone_no):
    if len(phone_no) != 11:
        raise ValidationError('The length of phone number is 11')
    else:
        return phone_no
