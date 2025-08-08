from django.core.management.base import BaseCommand
from builder.models import Role, Permission, RolePermission

class Command(BaseCommand):
    help = 'Seeds initial roles and permissions into the database.'

    def handle(self, *args, **options):
        # ✅ Create roles
        roles = ['Admin', 'Editor', 'Viewer']
        for role_name in roles:
            role_obj, created = Role.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Role created: {role_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Role already exists: {role_name}'))

        # ✅ Create permissions
        permissions = [
            ('View Dashboard', 'view_website'),
            ('Create Website', 'create_website'),
            ('Edit Website', 'edit_website'),
            ('Delete Website', 'delete_website'),
            ('Manage Users', 'manage_users'),
        ]

        for perm_name, codename in permissions:
            perm_obj, created = Permission.objects.get_or_create(name=perm_name, codename=codename)
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Permission created: {perm_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Permission already exists: {perm_name}'))

        # ✅ Assign all permissions to Admin role
        try:
            admin_role = Role.objects.get(name='Admin')
        except Role.DoesNotExist:
            self.stdout.write(self.style.ERROR("❌ Admin role not found."))
            return

        # ✅ Get or create RolePermission for Admin
        role_permission_obj, created = RolePermission.objects.get_or_create(role=admin_role)

        # ✅ Assign all permissions
        all_permissions = Permission.objects.all()
        role_permission_obj.permission.set(all_permissions)  # set() replaces all existing permissions
        role_permission_obj.save()

        self.stdout.write(self.style.SUCCESS('🎉 Admin role now has all permissions!'))
