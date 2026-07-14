from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # ── Auth JWT ─────────────────────────────────────────────────────────────
    path('token/',         TokenObtainPairView.as_view(), name='api_token'),
    path('token/refresh/', TokenRefreshView.as_view(),    name='api_token_refresh'),
    path('moi/',           views.api_moi,                 name='api_moi'),

    # ── Experts ───────────────────────────────────────────────────────────────
    path('experts/',              views.ExpertListAPIView.as_view(),   name='api_experts'),
    path('experts/<int:pk>/',     views.ExpertDetailAPIView.as_view(), name='api_expert_detail'),
    path('experts/<int:pk>/avis/', views.api_avis_expert,              name='api_avis_expert'),

    # ── Dossiers ──────────────────────────────────────────────────────────────
    path('dossiers/',                       views.DossierListCreateAPIView.as_view(), name='api_dossiers'),
    path('dossiers/<int:pk>/',              views.DossierDetailAPIView.as_view(),     name='api_dossier_detail'),
    path('dossiers/<int:pk>/messages/',     views.api_messages_dossier,               name='api_messages'),

    # ── ML ────────────────────────────────────────────────────────────────────
    path('recommander/', views.api_recommander, name='api_recommander'),
    path('chatbot/',     views.api_chatbot,     name='api_chatbot'),

    # ── Stats ─────────────────────────────────────────────────────────────────
    path('stats/',       views.api_stats,       name='api_stats'),
]