from django.contrib import admin
from django.urls import path, include


# handler404 = 'core.views.error_404'
# handler500 = 'core.views.error_500'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls'))
]
