from django.conf.urls import patterns, include, url
from django.contrib import admin

from authentication.views import AccountViewSet, LoginView, LogoutView

from rest_framework_nested import routers

router = routers.SimpleRouter()
router.register(r'accounts', AccountViewSet)

account_router = routers.NestedSimpleRouter(
    router, r'accounts', lookup='account'
)
urlpatterns = patterns('',
    # Examples:
    #url(r'^$', 'ciberonline.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/', include(account_router.urls)),
    url(r"api/v1/auth/login/$", LoginView.as_view(), name="login"),
    url(r'^api/v1/auth/logout/$', LogoutView.as_view(), name='logout'),
    
)
