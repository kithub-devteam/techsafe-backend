from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import UserProfile, Role, Cookie
from .serializers import (
    SignupSerializer, UserProfileSerializer, RoleSerializer,
    CookieSerializer, UserSerializer, LoginSerializer,
    PasswordResetSerializer, CustomTokenObtainPairSerializer
)
from .permissions import IsAdmin, IsResearcher, IsYouth
from rest_framework.decorators import api_view, permission_classes
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['destroy', 'create']:
            return [IsAdmin()]
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.idrole.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]
    

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.idrole.role == 'admin':
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

class CookieViewSet(viewsets.ModelViewSet):
    queryset = Cookie.objects.all()
    serializer_class = CookieSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cookie.objects.filter(user=self.request.user)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        print("Données reçues:", request.data)
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            
            # Générer le token
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(user).data
            })
            
        except serializers.ValidationError as e:
            print("Erreur de validation:", e.detail)
            return Response({
                'success': False,
                'message': e.detail.get('non_field_errors', ['Erreur de validation'])[0]
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            print("Erreur inattendue:", str(e))
            return Response({
                'success': False,
                'message': "Une erreur inattendue est survenue"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"message": "Déconnexion réussie"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"message": "Déconnexion réussie"}, status=status.HTTP_200_OK)

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        print("Données reçues:", request.data)
        
        # Créer une copie des données pour les modifier
        data = request.data.copy()
        
        # S'assurer que idrole est un entier
        if 'idrole' in data:
            try:
                role_id = int(data['idrole'])
                data['idrole'] = role_id
            except (ValueError, TypeError):
                return Response(
                    {'error': 'ID de rôle invalide'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            print("Erreurs de validation:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = serializer.save()
            token = CustomTokenObtainPairSerializer.get_token(user)
            return Response({
                'success': True,
                'access': str(token.access_token),
                'refresh': str(token),
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print("Erreur lors de la création de l'utilisateur:", e)
            return Response({
                'error': 'Erreur lors de la création du compte'
            }, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Mot de passe réinitialisé avec succès"},
            status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_roles(request):
    roles = Role.objects.filter(status='disponible')
    serializer = RoleSerializer(roles, many=True)
    return Response(serializer.data)