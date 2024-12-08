from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.utils.text import slugify


class UserManager(BaseUserManager):
    def create_user(self, password=None, **extra_fields):
        email = extra_fields.pop('email', None)  # On retire email des extra_fields
        phone_number = extra_fields.pop('phone_number', None)  # On retire phone_number des extra_fields
        username = extra_fields.pop('username', None)  # On retire username des extra_fields
        
        if not email and not phone_number:
            raise ValueError('Email ou numéro de téléphone requis')
            
        if email:
            email = self.normalize_email(email)
            
        # Créer l'utilisateur avec les champs extraits
        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
            
        user.set_password(password)
        user.save(using=self._db)
        
        if phone_number:
            UserProfile.objects.create(user=user, phone_number=phone_number)
            
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if not email:
            raise ValueError('Email requis pour superuser')
            
        role, created = Role.objects.get_or_create(
            role=Role.ADMIN,
            defaults={'status': 'disponible'}
        )
        extra_fields['idrole'] = role
        
        return self.create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields
        )
class Role(models.Model):
    JEUNE = 'jeune'
    CHERCHEUR = 'chercheur'
    ACTEUR_DIRECT = 'acteur_direct'
    ACTEUR_INDIRECT = 'acteur_indirect'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (JEUNE, 'Jeune'),
        (CHERCHEUR, 'Chercheur'),
        (ACTEUR_DIRECT, 'Acteur Direct'),
        (ACTEUR_INDIRECT, 'Acteur Indirect'),
        (ADMIN, 'Administrateur')
    ]
    ROLE_STATUS_CHOISE = (
         ('disponible','Disponible'),
         ('non-disponible','Non Disponible')
    )

    role = models.CharField(max_length=100, choices=ROLE_CHOICES,unique=True)
    slug = models.SlugField(max_length=100, null=True)
    status = models.CharField(max_length=100,choices=ROLE_STATUS_CHOISE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
            if not self.slug and self.role:
                self.slug = slugify(self.get_role_display())
            super(Role, self).save(*args, **kwargs)
    def __str__(self):
        return self.get_role_display()

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    username = models.CharField(max_length=100)
    idrole = models.ForeignKey('Role', on_delete=models.CASCADE, related_name='users', blank=True, null=True)
    idpart = models.ForeignKey('partners.Partner', on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'  # On garde email comme champ principal mais il sera optionnel
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        if hasattr(self, 'userprofile') and self.userprofile.phone_number:
            return self.userprofile.phone_number
        return self.email or ''

    

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.email and not hasattr(self, 'userprofile'):
            raise ValidationError("Email ou numéro de téléphone requis")
        if hasattr(self, 'userprofile') and not self.email and not self.userprofile.phone_number:
            raise ValidationError("Email ou numéro de téléphone requis")
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(unique=True, max_length=20, null=True)
    
    # Champs communs
    profile_picture = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    
    # Champs pour Entreprise
    company_name = models.CharField(max_length=200, null=True)
    registration_number = models.CharField(max_length=100, null=True)
    company_size = models.CharField(max_length=50, null=True)
    industry = models.CharField(max_length=100, null=True)
    
    # Champs pour ONG
    organization_name = models.CharField(max_length=200, null=True)
    registration_id = models.CharField(max_length=100, null=True)
    organization_type = models.CharField(max_length=100, null=True)
    focus_area = models.CharField(max_length=200, null=True)
    
    # Champs pour Personnel/Chercheur
    institution = models.CharField(max_length=200, null=True)
    position = models.CharField(max_length=100, null=True)
    specialization = models.CharField(max_length=200, null=True)
    research_interests = models.TextField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Cookie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(auto_now_add=True)
    cookie_data = models.TextField(null=True)
