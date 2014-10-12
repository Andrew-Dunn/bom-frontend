from django import template

register = template.Library()

@register.inclusion_tag('pagination.html')
def pagination(number, pages):
   return { 'number': number, 'pages' : pages }
