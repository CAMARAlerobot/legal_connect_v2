from rest_framework import generics, permissions, serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema, inline_serializer
from collaboration.models import Dossier
from .serializers import (
    UserSerializer, ExpertSerializer,
    DossierSerializer, DossierCreateSerializer,
    RecommandationRequestSerializer, ChatbotRequestSerializer,
)


@extend_schema(responses=UserSerializer)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_moi(request):
    """GET /api/moi/ — Profil de l'utilisateur connecté."""
    return Response(UserSerializer(request.user).data)


class ExpertListAPIView(generics.ListAPIView):
    """GET /api/experts/ — Liste des experts."""
    serializer_class   = ExpertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = User.objects.filter(
            profil__role='expert', is_active=True
        ).select_related('profil')
        specialite = self.request.query_params.get('specialite')
        ville      = self.request.query_params.get('ville')
        if specialite:
            qs = qs.filter(profil__specialite=specialite)
        if ville:
            qs = qs.filter(profil__adresse__icontains=ville)
        return qs


class ExpertDetailAPIView(generics.RetrieveAPIView):
    """GET /api/experts/<id>/ — Détail d'un expert."""
    serializer_class   = ExpertSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset           = User.objects.filter(profil__role='expert')


@extend_schema(responses=inline_serializer(
    name='AvisExpertResponse',
    fields={
        'id':          serializers.IntegerField(),
        'note':        serializers.IntegerField(),
        'commentaire': serializers.CharField(),
        'auteur':      serializers.CharField(),
        'date':        serializers.CharField(),
    },
    many=True,
))
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_avis_expert(request, pk):
    """GET /api/experts/<id>/avis/ — Avis d'un expert."""
    try:
        from annuaire.models import AvisExpert
        avis = AvisExpert.objects.filter(
            expert_id=pk, valide=True
        ).select_related('auteur').order_by('-created_at')
        data = [
            {
                'id':         a.id,
                'note':       a.note,
                'commentaire': a.commentaire,
                'auteur':     a.auteur.get_full_name() or a.auteur.username,
                'date':       a.created_at.strftime('%d/%m/%Y'),
            }
            for a in avis
        ]
        return Response(data)
    except Exception as e:
        return Response({'erreur': str(e)}, status=500)


class DossierListCreateAPIView(generics.ListCreateAPIView):
    """GET/POST /api/dossiers/"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DossierCreateSerializer
        return DossierSerializer

    def get_queryset(self):
        user   = self.request.user
        profil = getattr(user, 'profil', None)
        if profil and profil.role == 'expert':
            return Dossier.objects.filter(expert=user).order_by('-created_at')
        return Dossier.objects.filter(client=user).order_by('-created_at')

    def get_serializer_context(self):
        return {'request': self.request}


class DossierDetailAPIView(generics.RetrieveAPIView):
    """GET /api/dossiers/<id>/"""
    serializer_class   = DossierSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return (
            Dossier.objects.filter(client=user) |
            Dossier.objects.filter(expert=user)
        )


@extend_schema(responses=inline_serializer(
    name='MessageDossierResponse',
    fields={
        'id':      serializers.IntegerField(),
        'contenu': serializers.CharField(),
        'auteur':  serializers.CharField(),
        'lu':      serializers.BooleanField(),
        'date':    serializers.CharField(),
    },
    many=True,
))
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_messages_dossier(request, pk):
    """GET /api/dossiers/<id>/messages/"""
    try:
        from collaboration.models import Message
        dossier = Dossier.objects.get(pk=pk)
        if dossier.client != request.user and dossier.expert != request.user:
            return Response({'erreur': 'Accès refusé.'}, status=403)
        messages = Message.objects.filter(
            dossier=dossier
        ).select_related('auteur').order_by('created_at')
        data = [
            {
                'id':      m.id,
                'contenu': m.contenu,
                'auteur':  m.auteur.get_full_name() if m.auteur else '',
                'lu':      m.lu,
                'date':    m.created_at.strftime('%d/%m/%Y %H:%M'),
            }
            for m in messages
        ]
        return Response(data)
    except Dossier.DoesNotExist:
        return Response({'erreur': 'Dossier introuvable.'}, status=404)
    except Exception as e:
        return Response({'erreur': str(e)}, status=500)


@extend_schema(
    request=RecommandationRequestSerializer,
    responses=inline_serializer(
        name='RecommandationResponse',
        fields={
            'categorie': serializers.CharField(),
            'confiance': serializers.FloatField(),
            'experts':   ExpertSerializer(many=True),
        },
    ),
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def api_recommander(request):
    """POST /api/recommander/ — Recommandation IA."""
    serializer = RecommandationRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        from ml_recommandation.classifier import recommander_experts
        resultats = recommander_experts(
            texte      = serializer.validated_data['texte'],
            ville      = serializer.validated_data.get('ville', ''),
            limit      = 3,
        )
        experts_data = ExpertSerializer(
            [r['expert'] for r in resultats['experts']], many=True
        ).data
        return Response({
            'categorie': resultats['classification']['label'],
            'confiance': resultats['classification']['score_confiance'],
            'experts':   experts_data,
        })
    except Exception as e:
        return Response({'erreur': str(e)}, status=500)


@extend_schema(
    request=ChatbotRequestSerializer,
    responses=inline_serializer(
        name='ChatbotResponse',
        fields={
            'reponse':     serializers.CharField(),
            'intention':   serializers.CharField(),
            'confiance':   serializers.FloatField(),
            'escalade':    serializers.BooleanField(),
            'suggestions': serializers.ListField(child=serializers.CharField()),
        },
    ),
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def api_chatbot(request):
    """POST /api/chatbot/ — Chatbot juridique."""
    serializer = ChatbotRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    try:
        from chatbot.moteur import traiter_message
        reponse = traiter_message(serializer.validated_data['message'])
        return Response(reponse)
    except Exception as e:
        return Response({'erreur': str(e)}, status=500)


@extend_schema(responses=inline_serializer(
    name='StatsResponse',
    fields={
        'total_utilisateurs': serializers.IntegerField(),
        'total_experts':      serializers.IntegerField(),
        'total_dossiers':     serializers.IntegerField(),
        'dossiers_en_cours':  serializers.IntegerField(),
        'total_avis':         serializers.IntegerField(),
    },
))
@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def api_stats(request):
    """GET /api/stats/ — Statistiques (admin)."""
    try:
        from annuaire.models import AvisExpert
        return Response({
            'total_utilisateurs': User.objects.count(),
            'total_experts':      User.objects.filter(profil__role='expert').count(),
            'total_dossiers':     Dossier.objects.count(),
            'dossiers_en_cours':  Dossier.objects.filter(statut='en_cours').count(),
            'total_avis':         AvisExpert.objects.filter(valide=True).count(),
        })
    except Exception as e:
        return Response({'erreur': str(e)}, status=500)