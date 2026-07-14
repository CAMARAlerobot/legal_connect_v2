from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as accounts_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/',          admin.site.urls),
    path('accounts/',       include('accounts.urls')),
    path('contrats/',       include('contrats.urls')),
    path('documents/',      include('documents.urls')),
    path('fiscalite/',      include('fiscalite.urls')),
    path('collaboration/',  include('collaboration.urls')),
    path('notifications/',  include('notifications.urls')),
    path('annuaire/',       include('annuaire.urls')),
    path('dashboard/',      include('accounts.urls_dashboard')),
    path('recommandation/', include('ml_recommandation.urls')),
    path('chatbot/',        include('chatbot.urls')),
    path('abonnements/',    include('abonnements.urls')),
    path('api/',            include('api.urls')),
    path('api/schema/',     SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',       SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('',                accounts_views.landing, name='landing'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)