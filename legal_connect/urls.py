from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views

urlpatterns = [
    path('admin/',         admin.site.urls),
    path('accounts/',      include('accounts.urls')),
    path('contrats/',      include('contrats.urls')),
    path('documents/',     include('documents.urls')),
    path('fiscalite/',     include('fiscalite.urls')),
    path('collaboration/', include('collaboration.urls')),
    path('notifications/', include('notifications.urls')),
    path('annuaire/',      include('annuaire.urls')),
    path('dashboard/',     include('accounts.urls_dashboard')),
    path('',               accounts_views.landing, name='landing'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)