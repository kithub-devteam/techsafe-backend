from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from .models import User, UserProfile, Role, Cookie
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'idpart', 'idrole', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['date_joined']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class CookieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cookie
        fields = '__all__'
        read_only_fields = ['consent_date']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        login = data.get('login', '').strip()
        password = data.get('password', '')
        
        if not login or not password:
            raise serializers.ValidationError({
                "non_field_errors": "Tous les champs sont requis"
            })

        try:
            if '@' in login:
                # Email login attempt
                user = authenticate(username=login, password=password)
                if not user:
                    raise serializers.ValidationError({
                        "non_field_errors": "Email ou mot de passe incorrect"
                    })
            else:
                # Phone login attempt
                formatted_phone = login.strip().replace(' ', '')
                user = authenticate(username=formatted_phone, password=password)
                if not user:
                    raise serializers.ValidationError({
                        "non_field_errors": "Numéro de téléphone ou mot de passe incorrect"
                    })
            
            if not user.is_active:
                raise serializers.ValidationError({
                    "non_field_errors": "Ce compte a été désactivé"
                })
                
            data['user'] = user
            return data
            
        except Exception as e:
            if '@' in login:
                raise serializers.ValidationError({
                    "non_field_errors": "Email ou mot de passe incorrect"
                })
            else:
                raise serializers.ValidationError({
                    "non_field_errors": "Numéro de téléphone ou mot de passe incorrect"
                })
class SignupSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    
    # Champs spécifiques pour les différents types de compte
    # Entreprise (acteur_direct)
    company_name = serializers.CharField(required=False, write_only=True)
    registration_number = serializers.CharField(required=False, write_only=True)
    company_size = serializers.CharField(required=False, write_only=True)
    industry = serializers.CharField(required=False, write_only=True)
    
    # ONG (acteur_indirect)
    organization_name = serializers.CharField(required=False, write_only=True)
    registration_id = serializers.CharField(required=False, write_only=True)
    organization_type = serializers.CharField(required=False, write_only=True)
    focus_area = serializers.CharField(required=False, write_only=True)
    
    # Personnel/Chercheur
    institution = serializers.CharField(required=False, write_only=True)
    position = serializers.CharField(required=False, write_only=True)
    specialization = serializers.CharField(required=False, write_only=True)
    research_interests = serializers.CharField(required=False, write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'phone_number', 'username', 'password', 'password_confirm', 
                 'role', 'idrole', 'company_name', 'registration_number', 'company_size', 
                 'industry', 'organization_name', 'registration_id', 'organization_type', 
                 'focus_area', 'institution', 'position', 'specialization', 'research_interests')
        extra_kwargs = {
            'password': {'write_only': True},
            'idrole': {'required': True},
            'email': {'required': False},
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas")
        
        if not data.get('email') and not data.get('phone_number'):
            raise serializers.ValidationError("Email ou numéro de téléphone requis")
            
        try:
            role_id = data.get('idrole')
            role_name = data.get('role')
            
            if isinstance(role_id, Role):
                role = role_id
                role_id = role.id
            else:
                role_id = int(role_id)
                role = Role.objects.get(id=role_id)
            
            if role.role != role_name:
                raise serializers.ValidationError(
                    f"Le type de compte sélectionné ({role_name}) ne correspond pas"
                )
            
            # Validation des champs spécifiques selon le rôle
            if role.role == Role.ACTEUR_DIRECT:
                required_fields = ['company_name', 'registration_number', 'industry']
                for field in required_fields:
                    if not data.get(field):
                        raise serializers.ValidationError(f"Le champ {field} est requis pour une entreprise")
                        
            elif role.role == Role.ACTEUR_INDIRECT:
                required_fields = ['organization_name', 'registration_id', 'focus_area']
                for field in required_fields:
                    if not data.get(field):
                        raise serializers.ValidationError(f"Le champ {field} est requis pour une ONG")
                        
            elif role.role == Role.CHERCHEUR:
                required_fields = ['institution', 'position', 'specialization']
                for field in required_fields:
                    if not data.get(field):
                        raise serializers.ValidationError(f"Le champ {field} est requis pour un chercheur")
                
            data['idrole'] = role_id
            
        except (ValueError, TypeError) as e:
            raise serializers.ValidationError("ID de rôle invalide")
        except Role.DoesNotExist:
            raise serializers.ValidationError("Type de compte non trouvé")
        
        return data

    def create(self, validated_data):
        try:
            # Extraire les données de base
            password = validated_data.pop('password')
            validated_data.pop('password_confirm')
            role_name = validated_data.pop('role')
            phone_number = validated_data.pop('phone_number', None)
            
            # Extraire les données spécifiques au profil
            profile_data = {}
            profile_fields = []
            
            if role_name == Role.ACTEUR_DIRECT:
                profile_fields = ['company_name', 'registration_number', 'company_size', 'industry']
            elif role_name == Role.ACTEUR_INDIRECT:
                profile_fields = ['organization_name', 'registration_id', 'organization_type', 'focus_area']
            elif role_name == Role.CHERCHEUR:
                profile_fields = ['institution', 'position', 'specialization', 'research_interests']
            
            for field in profile_fields:
                if field in validated_data:
                    profile_data[field] = validated_data.pop(field)
            
            # Créer l'utilisateur
            user = User(
                username=validated_data.pop('username'),
                email=validated_data.get('email'),
                idrole_id=validated_data.pop('idrole')
            )
            user.set_password(password)
            user.save()
            
            # Créer le profil avec toutes les données
            if phone_number or profile_data:
                profile_data['phone_number'] = phone_number
                UserProfile.objects.create(user=user, **profile_data)
            
            return user
            
        except Exception as e:
            print(f"Erreur détaillée lors de la création: {str(e)}")
            raise serializers.ValidationError(f"Erreur lors de la création du compte: {str(e)}")


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        
        try:
            self.user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Aucun utilisateur trouvé avec cet email.")
        
        return data

    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.save()
        return self.user