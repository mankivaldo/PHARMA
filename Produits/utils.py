from django.core.exceptions import PermissionDenied

def role_required(*roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if hasattr(request.user, 'role') and request.user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("Vous n'avez pas les droits nécessaires.")
        return _wrapped_view
    return decorator