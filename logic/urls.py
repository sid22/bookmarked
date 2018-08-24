from django.conf.urls import url, include
from . import views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', views.index_page, name="index"),
    url(r'^bookmarks/add', views.add_bookmark, name="add"),
    url(r'^bookmarks/delete', views.delete_bookmark, name="delete"),
]
