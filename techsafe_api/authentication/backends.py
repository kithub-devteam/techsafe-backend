from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User, UserProfile

class EmailPhoneAuthBackend(ModelBackend):
    def _format_phone_number(self, phone):
        if not phone:
            return phone
        phone = str(phone).strip().replace(' ', '')
        if phone.startswith('0'):
            phone = '+257' + phone[1:]
        elif not phone.startswith('+'):
            phone = '+257' + phone
        return phone

    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            print(f"Tentative d'authentification - Username original: {username}")
            
            if '@' in str(username):
                # Recherche par email
                user = User.objects.get(email=username)
                print(f"Recherche par email: {user.username}")
            else:
                # Formater et rechercher par numéro de téléphone
                formatted_phone = self._format_phone_number(username)
                print(f"Numéro formaté: {formatted_phone}")
                
                try:
                    # Essayer avec le numéro formaté
                    profile = UserProfile.objects.select_related('user').get(phone_number=formatted_phone)
                    print(f"Profil trouvé avec numéro formaté")
                except UserProfile.DoesNotExist:
                    # Essayer avec le numéro original
                    try:
                        profile = UserProfile.objects.select_related('user').get(phone_number=username)
                        print(f"Profil trouvé avec numéro original")
                    except UserProfile.DoesNotExist:
                        print("Aucun profil trouvé")
                        return None
                
                user = profile.user
                print(f"Utilisateur trouvé: {user.username}")

            if user.check_password(password):
                print("Mot de passe correct")
                return user
            print("Mot de passe incorrect")
            return None

        except Exception as e:
            print(f"Erreur d'authentification: {str(e)}")
            return None


    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
        