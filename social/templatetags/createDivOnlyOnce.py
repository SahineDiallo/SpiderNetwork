from django import template
from datetime import datetime, timedelta
from django import template
from django.utils.timesince import timesince
from django.utils import timezone

register = template.Library()


@register.filter(name="create_first_div_once")
def create_first_div_once(index):
    return True if index == 3 else False


@register.filter(name="create_second_div_once")
def create_second_div_once(index):
    return True if index == 1 else False


@register.filter
def first_date_letter(value):
    now = timezone.now()
    try:
        difference = now - value
    except:
        return value

    if difference <= timedelta(minutes=1):
        return 'just now'
    result = '%(time)s ago' % {'time': timesince(value).split(', ')[0]}
    l = result.split(" ")
    l_sec = l[0].split("\xa0")
    l_sec[1] = l_sec[1][:1]  # get only the first letter of the second part
    l[0] = "".join(l_sec)
    return " ".join(l)


@register.filter(name="two_last_comments")
def two_last_comments(queryset):
    return queryset.order_by("-id")[:2]
