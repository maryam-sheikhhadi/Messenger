from django.core.exceptions import ValidationError


def validate_file_size(value):
    filesize = value.size

    if filesize > 26214400:
        raise ValidationError("The maximum file size that can be uploaded is 25MB")
    else:
        return value

def validate_email(value):
    pass