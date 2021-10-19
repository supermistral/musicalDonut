from django import template


register = template.Library()


@register.simple_tag
def music_links(widgets):
    result = []
    for ref_key, ref_value in widgets:
        if ref_value:
            result.append({
                "link_key": ref_key,
                "link_value": ref_value
            })
    return result