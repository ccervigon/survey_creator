# -*- coding: utf-8 -*- 

from django.shortcuts import render_to_response
from models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
import random

text_error = ''

@csrf_exempt
def welcome(request, author_hash=None):
    request.session.set_expiry(0)
    if request.method == 'GET':
        if author_hash == None:
            form = AuthorForm()
            try:
                del request.session['_author_hash']
            except:
                pass
            text_error = ''
        else:
            if not Author.objects.filter(author_hash=author_hash).exists():
                return HttpResponseRedirect('/')
            request.session['_author_hash'] = author_hash
            return HttpResponseRedirect('/survey')
    elif request.method == 'POST':
        form = AuthorForm(request.POST)
        try:
            aut_form = form.save(commit=False)
            Author.objects.get(name__iexact=aut_form.name)
            request.session['_old_post'] = request.POST
            request.session['_param'] = 'name'
            return HttpResponseRedirect('/survey')
        except:
            if Author.objects.filter(email__iexact=aut_form.email).exists() and \
            Author.objects.filter(email__iexact=aut_form.email)[0].email != '':
                request.session['_old_post'] = request.POST
                request.session['_param'] = 'email'
                return HttpResponseRedirect('/survey')
            text_error = 'Please check your name and email because \
                        you don\'t appear in the author list'

    response = render_to_response('login.html', 
                                  {'form': form, 'error': text_error},
                                  context_instance=RequestContext(request))
    return response

@csrf_exempt
def survey(request):
    if request.method == 'GET':
        author_hash = request.session.get('_author_hash', None)
        if author_hash != None:
            author = Author.objects.filter(author_hash=author_hash).reverse()[0]
        else:
            form = AuthorForm(request.session.get('_old_post'))
            aut_form = form.save(commit=False)
            param = request.session.get('_param')
            if param == 'name':
                author = Author.objects.get(name__iexact=aut_form.name)
            elif param == 'email':
                author = Author.objects.filter(email__iexact=aut_form.email).reverse()[0]
            else:
                return HttpResponseRedirect('/')

        request.session['_author'] = author.author_hash
        rand = random.randint(0,1)
        if rand == 0:
            type_survey = 1
            flag_fig = True
            flag_info = True
            figure = author.fig_name + '.png'
        else:
            type_survey = 2
            flag_fig = False
            flag_info = False
            figure = ''
        project = author.project
        project = project[:project.rfind('_')]
        response = render_to_response('survey.html',
                                      {'survey': type_survey,
                                       'flag_fig': flag_fig,
                                       'flag_info': flag_info,
                                       'figure': figure,
                                       'project': project},
                                       context_instance=RequestContext(request))
        return response
    elif request.method == 'POST':
        form = Survey1Form(request.POST)
        survey_form = form.save(commit=False)
        author_hash = request.session.get('_author')
        author = Author.objects.filter(author_hash=author_hash).reverse()[0]
        survey = Survey_author(author=author,
                           upeople_id=author.upeople_id,
                           project=author.project,
                           resp1=survey_form.resp1,
                           resp2=survey_form.resp2,
                           resp3=survey_form.resp3,
                           resp4=survey_form.resp4,
                           resp5=survey_form.resp5,
                           info=survey_form.info,
                           type_survey=1)
        survey.save()
        return HttpResponseRedirect('/thanks')
    return HttpResponseRedirect('/')

@csrf_exempt
def survey2(request):
    try:
        del request.session['_sec_post']
        form = Survey2Form(request.session.get('_first_post'))
        first_post = form.save(commit=False)
        form = Survey2bForm(request.POST)
        second_post = form.save(commit=False)
        author_hash = request.session.get('_author')
        author = Author.objects.filter(author_hash=author_hash).reverse()[0]
        survey = Survey_author(author=author,
                           upeople_id=author.upeople_id,
                           project=author.project,
                           resp1=first_post.resp1,
                           resp2=first_post.resp2,
                           resp3=first_post.resp3,
                           resp4=second_post.resp4,
                           resp5=second_post.resp5,
                           info=second_post.info,
                           type_survey=2)
        survey.save()
        return HttpResponseRedirect('/thanks')
    except:
        request.session['_first_post'] = request.POST
        request.session['_sec_post'] = True
        author_hash = request.session.get('_author')
        author = Author.objects.filter(author_hash=author_hash).reverse()[0]
        figure = author.fig_name + '.png'
        project = author.project
        project = project[:project.rfind('_')]
        response = render_to_response('survey2.html',
                                      {'figure': figure,
                                       'project': project},
                                      context_instance=RequestContext(request))
        return response

def thanks(request):
    request.session.flush()
    return render_to_response('thanks.html',
                              context_instance=RequestContext(request))

def result(request):
    return render_to_response('result.html',
                              context_instance=RequestContext(request))

def information(request):
    return render_to_response('information.html',
                              context_instance=RequestContext(request))

def privacy(request):
    return render_to_response('privacy.html',
                              context_instance=RequestContext(request))

def contact(request):
    return render_to_response('contact.html',
                              context_instance=RequestContext(request))
