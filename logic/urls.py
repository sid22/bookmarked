from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index_page, name="index"),
    url(r'^bookmarks/add', views.add_bookmark, name="add"),
    url(r'^bookmarks/delete', views.delete_bookmark, name="delete"),
    url(r'^bookmarks/edit', views.edit_bookmark, name="edit"),
    url(r'^labels/edit', views.edit_label, name="edit_label"),
    url(r'^labels/create', views.create_label, name="create_label"),
    url(r'^labels', views.manage_label, name="manage_label"),
    url(r'^login', views.login_view, name="login"),
    url(r'^logout', views.logout_view, name="logout")
]
