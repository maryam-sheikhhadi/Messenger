from django.core.exceptions import ValidationError


def validate_file_size(file):
    filesize = file.size

    if filesize > 26214400:
        raise ValidationError("The maximum file size that can be uploaded is 25MB")
    else:
        return file
