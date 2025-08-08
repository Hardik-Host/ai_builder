from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=10, default='Viewer')

    def __str__(self):
        return self.name
    
class Permission(models.Model):
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ManyToManyField(Permission, related_name='roles')

class User(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.role:
            try:
                self.role = Role.objects.get(name='Admin')
            except Role.DoesNotExist:
                pass
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.username

class Website(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    content_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)