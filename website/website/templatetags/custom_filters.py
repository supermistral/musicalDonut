from django.template.defaulttags import register


@register.filter
def get_item(input_dict, key):
    return input_dict.get(key)