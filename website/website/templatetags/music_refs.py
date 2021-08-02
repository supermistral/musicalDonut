from django import template


register = template.Library()


@register.simple_tag
def music_refs(**kwargs):
    result = []
    for ref_key, ref_value in kwargs.items():
        result.append({
            "refkey": ref_key,
            "refvalue": ref_value
        })
    return result