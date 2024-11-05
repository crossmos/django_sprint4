from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.urls import path, include, reverse_lazy


# handler404 = 'core.views.error_404'
# handler500 = 'core.views.error_500'

urlpatterns = [
    path('', include('blog.urls')),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index')
        ),
        name='registration'
    ),
    path('pages/', include('pages.urls'))
]
