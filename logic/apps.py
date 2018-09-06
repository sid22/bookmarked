# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.conf import settings

from .database import db


class LogicConfig(AppConfig):
    name = 'logic'
    def ready(self):
        db.configs.find_one_and_update(
            {"set_password": "yes"}, 
            { '$set': {"password": settings.BASE_PASSWORD} }, 
            upsert=True)
        pass
