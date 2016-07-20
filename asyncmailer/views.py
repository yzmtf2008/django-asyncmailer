from asyncmailer.tasks import async_mail
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
import json
import os
import re


def get_options():
    try:
        templatepath = settings.ASYNCMAILER_TEMPLATES_PATH
    except:
        templatepath = os.path.dirname(__file__) + '/templates/asyncmailer/'
    templates = []

    for dirname in os.listdir(templatepath):
        if (not os.path.isdir(templatepath + dirname)):
            continue
        else:
            new_template = {"dir": dirname, "html": "", "variations": []}
            for filename in os.listdir(templatepath + dirname):
                if (re.findall('\.html$', filename)):
                    new_template['html'] = filename
                elif (re.findall('\.json$', filename)):
                    new_template['variations'].append(filename)
                else:
                    pass
            templates.append(new_template)
    return templates


def get_form(request):
    try:
        template = request.POST.get('template', '')
        variation = request.POST.get('variation', '')
        locale = request.POST.get('locale', '')
        inline = request.POST.get('inline', '')
        formats = request.POST.get('format', '')
        payload = request.POST.get('payload', '{}')
        if (payload):
            payload = json.loads(payload)
        else:   # jsons
            payload = {}
        return (template, variation, locale, inline, formats, payload)
    except:
        return None


@staff_member_required
def index(request):
    templates = [i['html'] for i in get_options()]
    return render(request, 'asyncmailer/index.html', {'templates': templates})


@staff_member_required
def get_variations(request):
    template = request.POST.get('template', '')
    for i in get_options():
        if (i['html'] == template):
            variations = i['variations']
            break
    return HttpResponse(' '.join(variations))


@staff_member_required
def get_json(request):
    template = request.POST.get('template', '')
    variation = request.POST.get('variation', '')
    response = {}
    if (variation != 'base.json'):
        base_json = render_to_string(
            'asyncmailer/' + template.replace('.html', '-templates/base.json'))
        response.update(json.loads(str(base_json)))
    variation_json = render_to_string(
        'asyncmailer/' + template.replace('.html', '-templates/') + variation)
    response.update(json.loads(str(variation_json)))
    return HttpResponse(json.dumps(response))


@staff_member_required
def retrieve(request):
    template, variation, locale, inline, formats, payload = get_form(request)
    return render(request, 'asyncmailer/' +
                  template.replace('.html', '-templates/') + template, payload)


@staff_member_required
def presend(request):
    template, variation, locale, inline, formats, payload = get_form(request)
    email = request.POST.get('email', '')
    async_mail([email], "New Activity on Your Account",
               context_dict={"message": "\"%s\"" % payload.get('message'),
                             "button_text": payload.get('button_text'),
                             "button_url": "%s" % payload.get('button_url')},
               template='asyncmailer/' +
                        template.replace('.html', '-templates/') + template)
    return render(request, 'asyncmailer/index.html', payload)
