from django.http import JsonResponse
from django.urls import resolve
from .models import RolePermission

WHITELIST_URL_NAMES = ['login', 'register', 'logout']

class RolePermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # ✅ Skip check if user is not logged in
        if not request.user.is_authenticated:
            return self.get_response(request)

        role = request.user.role
        if not role:
            return JsonResponse({'error': 'User role not assigned'}, status=403)

        # ✅ Try to get the view name
        try:
            url_name = resolve(request.path_info).url_name
        except Exception:
            return self.get_response(request)  # skip if view doesn't resolve
        
        if url_name in WHITELIST_URL_NAMES:
            return self.get_response(request)

        # ✅ Skip URLs without url_name (like static, media, admin, etc.)
        if url_name is None:
            return self.get_response(request)

        # ✅ Admin role has full access
        if role.name.lower() == 'admin':
            return self.get_response(request)

        # ✅ Check if permission exists for this role and view
        try:
            role_permission = RolePermission.objects.get(role=role)
            if not role_permission.permission.filter(codename=url_name).exists():
                return JsonResponse({'error': 'Permission denied for this view'}, status=403)
        except RolePermission.DoesNotExist:
            return JsonResponse({'error': 'No permissions assigned for role'}, status=403)

        return self.get_response(request)
