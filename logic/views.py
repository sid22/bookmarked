# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import re
import time
import uuid

import jwt
from django.conf import settings
from django.shortcuts import redirect, render

from .database import db
from .database import redis_connection as red


def getepoch():
    orig = datetime.datetime.fromtimestamp(1425917335)
    new = orig + datetime.timedelta(days=30)
    return new

def authenticate_user(password):
    db_return = db.configs.find_one({"set_password": "yes"})
    if (password == db_return["password"]):
        uid = str(uuid.uuid4())
        token = jwt.encode({'user_id': uid, 'exp': getepoch()}, settings.JWT_SECRET_KEY, algorithm='HS256')
        db.auth_users.insert({"session_tok": token})
        red.set(str(token), 'logged')
        return {"valid": 1, "token": token}
    else:
        return {"valid": 0}

def is_authenticated(request):
    token = str(request.COOKIES.get('token',''))
    red_return = red.get(token)
    if red_return is None:
        check = db.auth_users.find_one({"session_tok": token})
        if check == None:
            return False
        else:
            try:
                jwt.decode(token, settings.JWT_SECRET_KEY, algorithm='HS256')
                red.set(token, 'logged')
                return True
            except jwt.ExpiredSignatureError:
                return False
    else:
        return True

def login_view(request):
    if request.method == 'POST':
        password = request.POST.get('password', '')
        authenticate_return = authenticate_user(password)
        if authenticate_return['valid'] == 0:
            context = {
                "error": "Incorrect password"
            }
            response = redirect('login')
            return response
        elif authenticate_return['valid'] == 1:
            context = {
                "success": "Succesfully authenticated"
            }
            response = redirect('index')
            response.set_cookie(key='token', value=authenticate_return['token'], max_age=2700000, secure=settings.COOKIE_SECURE) 
            return response
    else:
        context = {
            "no_session": True
        }
        return render(request, 'login.html', context)
    
def logout_view(request):
    token = str(request.COOKIES.get('token',''))
    db.auth_users.remove({"session_tok": token})
    red.delete(token)
    response = redirect('login')
    response.delete_cookie('token')
    return response

def check_url(input_url):
    a = re.match("^(http|https)://", input_url)
    if a:
        return input_url
    else:
        return ("http://" + input_url)

# Create your views here.
def index_page(request):
    '''
    View to display all the bookmarks
    '''
    if not is_authenticated(request):
        return redirect('login')
    label = request.GET.get('label', '')
    labels_list = list(db.labels.find({}))
    if label == '':  
        bookmark_list = list(db.bookmarks.find({}))[::-1]
        context = {
            "bookmark_list": bookmark_list,
            "labels_list": labels_list
        }
        alert_context = {
            "alert": True,
            "alert_type": "Success",
            "alert_message": "You have been authenticated!"
        }
        context = {**context, **alert_context}
    else:
        bookmark_list = list(db.bookmarks.find({"label": label}))
        context = {
            "label_name": label,
            "bookmark_list": bookmark_list,
            "labels_list": labels_list
        }
        alert_context = {
            "alert": True,
            "alert_type": "success",
            "alert_message": "You have been authenticated!"
        }
        context = {**context, **alert_context}
    response = render(request, "index.html", context)
    return response

def add_bookmark(request):
    '''
    View to add a bookmark
    '''
    if not is_authenticated(request):
        return redirect('login')
    if request.method == 'GET':
        unique_id = request.GET.get("id", '')
        if unique_id == '':
            label_list = list(db.labels.find({}))
            context = {
                "label_list": label_list
            }
            return render(request, "add.html", context=context)
        else:
            past_data = db.bookmarks.find_one({"unique_id": unique_id})
            label_list = list(db.labels.find({}))
            context = {
                "name": past_data["name"],
                "url": past_data["url"],
                "notes": past_data["notes"],
                "label": past_data["label"],
                "label_list": label_list,
                "id": unique_id
            }
            return render(request, "edit.html", context=context)

    elif request.method == 'POST':
        url = request.POST.get('url','')
        name = request.POST.get('name','')
        label = request.POST.get('label','')
        db_label = db.labels.find_one({"name": label})
        if db_label == None:
            to_insert = {
                "name": label,
                "unique_id": str(uuid.uuid4())
            }
            db.labels.insert(to_insert)
        
        notes = request.POST.get('notes','')
        url = check_url(url)
        to_insert = {
            "name": name,
            "url": url,
            "label": label,
            "notes": notes,
            "time":time.time(),
            "unique_id" : str(uuid.uuid4())
        }
        db.bookmarks.insert(to_insert)
        return redirect('index')

def edit_bookmark(request):
    '''
    View to edit a bookmark
    '''
    if not is_authenticated(request):
        return redirect('login')
    url = request.POST.get('url', '')
    name = request.POST.get('name', '')
    label = request.POST.get('label', '')
    notes = request.POST.get('notes', '')
    url = check_url(url)
    unique_id = request.POST.get('unique_id', '')
    to_update = {
        "name": name,
        "url": url,
        "label": label,
        "notes": notes,
        "time":time.time()
    }
    db.bookmarks.update({"unique_id": unique_id}, {"$set": to_update })
    return redirect("index")

def delete_bookmark(request):
    '''
    View to delete bookmark/label from it's mongo oid
    '''
    if not is_authenticated(request):
        return redirect('login')
    delete_id = request.GET.get('id','')
    delete_table = request.GET.get('thing', '')
    delete_type = request.GET.get('type','')
    if delete_table == 'bookmark':
        result = db.bookmarks.delete_one({'unique_id': delete_id})
    elif delete_table == 'labels':
        name = db.labels.find_one_and_delete({'unique_id': delete_id})["name"]
        if delete_type == 'labelonly':
            updates = db.bookmarks.update({'label':name}, {"$set": {'label':"Default"}}, multi=True)
        elif delete_type == 'labelandbookmarks':
            deletes = db.bookmarks.delete_many({"label":name})
    return redirect('index')

def create_label(request):
    '''
    View to create a new label to be used for bookmarks
    '''
    if not is_authenticated(request):
        return redirect('login')
    if request.method == 'GET':
        return render(request, "create_label.html")
    elif request.method == 'POST':
        label = request.POST.get('name','')
        to_insert = {
            "name": label,
            "unique_id": str(uuid.uuid4())
        }
        existing = db.labels.find_one({"name": label})
        if existing == None:
            db.labels.insert(to_insert)
        return redirect('index')

def manage_label(request):
    '''
    View to manage labels
    '''
    if not is_authenticated(request):
        return redirect('login')
    if request.method == 'GET':
        labels = db.labels.find({})
        context = {
            "labels" : labels
        }
        return render(request, "manage_labels.html", context=context)

def edit_label(request):
    '''
    Edit label
    '''
    if not is_authenticated(request):
        return redirect('login')
    if request.method == 'GET':
        unique_id = request.GET.get('id','')
        label_name = db.labels.find_one({"unique_id": unique_id})
        context = {
            "name": label_name["name"],
            "unique_id": label_name["unique_id"]
        }
        return render(request, "edit_label.html", context=context)
    elif request.method == 'POST':
        unique_id = request.POST.get('unique_id', '')
        new_name = request.POST.get('name', '')
        old_name = request.POST.get('old_name', '')
        db.bookmarks.update({"label": old_name},{"$set": {'label': new_name}}, multi=True)
        db.labels.update({"unique_id":  unique_id}, {"$set": {'name': new_name}})
        return redirect("index")
