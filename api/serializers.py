from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import Profil


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Profil
        fields = ['role', 'telephone', 'entreprise', 'specialite']


class UserSerializer(serializers.ModelSerializer):
    profil      = ProfilSerializer(read_only=True)
    nom_complet = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'first_name', 'last_name',
                  'email', 'nom_complet', 'profil']

    def get_nom_complet(self, obj) -> str:
        return obj.get_full_name() or obj.username


class ExpertSerializer(serializers.ModelSerializer):
    profil       = ProfilSerializer(read_only=True)
    nom_complet  = serializers.SerializerMethodField()
    note_moyenne = serializers.SerializerMethodField()
    nb_avis      = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'nom_complet', 'email', 'profil',
                  'note_moyenne', 'nb_avis']

    def get_nom_complet(self, obj) -> str:
        return obj.get_full_name() or obj.username

    def get_note_moyenne(self, obj) -> float:
        try:
            from annuaire.models import AvisExpert
            from django.db.models import Avg
            result = AvisExpert.objects.filter(
                expert=obj, valide=True
            ).aggregate(Avg('note'))
            return round(result['note__avg'] or 0, 1)
        except Exception:
            return 0

    def get_nb_avis(self, obj) -> int:
        try:
            from annuaire.models import AvisExpert
            return AvisExpert.objects.filter(expert=obj, valide=True).count()
        except Exception:
            return 0


class DossierSerializer(serializers.ModelSerializer):
    client_nom = serializers.SerializerMethodField()
    expert_nom = serializers.SerializerMethodField()

    class Meta:
        from collaboration.models import Dossier
        model  = Dossier
        fields = ['id', 'titre', 'description', 'statut',
                  'client_nom', 'expert_nom', 'created_at']

    def get_client_nom(self, obj) -> str:
        try:
            return obj.client.get_full_name() or obj.client.username
        except Exception:
            return ''

    def get_expert_nom(self, obj) -> str | None:
        try:
            return obj.expert.get_full_name() if obj.expert else None
        except Exception:
            return None


class DossierCreateSerializer(serializers.ModelSerializer):
    class Meta:
        from collaboration.models import Dossier
        model  = Dossier
        fields = ['titre', 'description']

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        validated_data['statut'] = 'en_cours'
        return super().create(validated_data)


class RecommandationRequestSerializer(serializers.Serializer):
    texte      = serializers.CharField(min_length=10)
    ville      = serializers.CharField(required=False, default='')
    budget_max = serializers.IntegerField(required=False, allow_null=True)


class ChatbotRequestSerializer(serializers.Serializer):
    message    = serializers.CharField(min_length=1)
    session_id = serializers.CharField(required=False, default='')