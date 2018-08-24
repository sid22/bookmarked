# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from database import db
from bson.objectid import ObjectId

import re, time

def check_url(input_url):
    a = re.match("^(http|https)://", input_url)
    if a:
        return input_url
        # print "match"
    else:
        return ("http://"+input_url)

# Create your views here.
def index_page(request):
    '''
    View to display all the bookmarks
    '''
    labels_list = list(db.labels.find({}))
    bookmark_list = list(db.bookmarks.find({}))
    context = {
        "bookmark_list": bookmark_list,
        "labels_list": labels_list
    }
    return render(request, "index.html", context)

def add_bookmark(request):
    '''
    View to add a bookmark
    '''
    if request.method == 'GET':
        return render(request, "add.html")
    elif request.method == 'POST':
        url = request.POST.get('url','')
        name = request.POST.get('name','')
        label = request.POST.get('label','')
        notes = request.POST.get('notes','')
        url = check_url(url)
        to_insert = {
            "name": name,
            "url": url,
            "label": label,
            "notes": notes,
            "time":time.time()
        }
        db.bookmarks.insert(to_insert)
        return redirect('index')

def delete_bookmark(request):
    '''
    View to delete bookmark from it's mongo oid
    '''    
    delete_id = request.GET.get('id','')
    result = db.bookmarks.delete_one({'_id': ObjectId(delete_id)})
    return redirect('index')