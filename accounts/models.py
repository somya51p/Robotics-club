from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone
from django.db.models.signals import post_save
from django.contrib import messages
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.username = username
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password,username):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            username,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password,username):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            username,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(PermissionsMixin, AbstractBaseUser):
    """
    Custom user model, with as the primary field for signin
    """

    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    username = models.CharField(max_length=250,unique=True)
    signup_time = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # a admin user; non super-user
    is_admin = models.BooleanField(default=False) # a superuser
    # notice the absence of a "Password field", that's built in.

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # Email & Password are required by default.


    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def if_staff(self):
        "Is the user a member of staff?"
        return self.is_staff

    @property
    def if_admin(self):
        "Is the user a admin member?"
        return self.is_admin

    @property
    def if_active(self):
        "Is the user active?"
        return self.is_active

    objects = UserManager()


class Profile(models.Model):
    """
    Store data of all users including the team members.
    """

    user_id = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userProfile")
    full_name = models.CharField(max_length=350)
    batch = models.CharField(max_length=4)
    phone = models.CharField(max_length=10)
    avatar = models.ImageField(upload_to='Members/')
    bio = models.TextField()

    class Meta:
        verbose_name_plural = "Member Profiles"

    def __str__(self):
        return f'{self.full_name} - {self.user_id.email}'