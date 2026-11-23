from django import template
from django.template.loader import render_to_string
from django.urls import resolve
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def Button(type='button', text=None, size='small', style='fill', has_icon=False, is_rounded=True):
    """
        style = fill, border, shadow
        size = small, medium, large
    """
    classes = 'rounded-pill '

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

    if is_rounded is False:
        classes = classes.replace('rounded-pill', 'rounded-lg')

    label = text or 'Button'
    icon_html = mark_safe('<img src="" alt="button icons">') if has_icon else mark_safe('')
    return format_html(
        '<button type="{}" class="{} flex items-center gap-3 duration-100 transition-all">{}{}</button>',
        type,
        classes,
        label,
        icon_html,
    )


@register.simple_tag(takes_context=True)
def active_class(context, url_name):
    request = context['request']
    current_url_name = resolve(request.path_info).url_name
    return 'text-primary' if current_url_name == url_name else ' text-gray-500'


@register.simple_tag(takes_context=True)
def dashboard_nav_class(context, url_name):
    request = context['request']
    try:
        current_url_name = resolve(request.path_info).url_name
    except Exception:
        current_url_name = None
    base = 'dashboard-nav-link'
    if current_url_name == url_name:
        return f'{base} dashboard-nav-link-active'
    return base


@register.simple_tag(takes_context=True)
def breadcrumb(context):
    request = context['request']
    path = request.path.strip('/').split('/')

    breadcrumb_items = [{'name': 'Home', 'url': '/'}]

    for i in range(len(path)):
        if not path[i]:
            continue
        breadcrumb_items.append({
            'name': path[i].capitalize(),
            'url': '/' + '/'.join(path[:i + 1]) + '/',
        })

    return render_to_string(
        'partials/breadcrumb.html',
        {'breadcrumb_items': breadcrumb_items},
        request=request,
    )