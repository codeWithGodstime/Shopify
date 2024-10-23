from django import template
from django.urls import resolve, reverse
from django.utils.html import format_html


register = template.Library()

@register.inclusion_tag('partials/buttons.html')
def Button(type='button', text=None, size='small', style='fill', has_icon=False, is_rounded=True):
    """
        style = fill, border, shadow
        size = small, medium, large

    """
    classes = 'rounded-4xl '

    if size == 'small':
        classes += 'px-5 py-1'
    elif size == 'medium':
        classes += 'px-8 py-1.5'
    elif size == 'large':
        classes += 'px-12 py-2' 

    if style == 'fill':
        classes += ' bg-primary text-white hover:bg-primary-hard'
    elif style == 'border':
        classes += ' bg-white border-2 border-primary text-primary hover:border-primary-hard hover:text-primary-hard'
    elif style == 'shadow':
        classes += ' bg-[#56AC591A] text-primary hover:text-primary-hard hover:bg-[#2C742F33]'

    if is_rounded == False:
        classes = classes.replace('rounded-4xl', '')
    print(classes)
    return {
        'text': text,
        'size': size,
        'style': style,
        'classes': classes,
        'has_icon': has_icon, 
        'type': type
        }


@register.simple_tag(takes_context=True)
def active_class(context, url_name):
    request = context['request']
    current_url_name = resolve(request.path_info).url_name
    return 'text-primary' if current_url_name == url_name else ' text-gray-500'

@register.inclusion_tag('partials/breadcrumb.html', takes_context=True)
def breadcrumb(context):
    request = context['request']
    path = request.path.strip('/').split('/')
    
    # Prepare breadcrumb items
    breadcrumb_items = [{'name': 'Home', 'url': '/'}]  # Home link
    
    for i in range(len(path)):
        breadcrumb_items.append({
            'name': path[i].capitalize(),
            'url': '/' + '/'.join(path[:i + 1]) + '/'
        })
    print(breadcrumb_items)
    return {
        'breadcrumb_items': breadcrumb_items
    }
