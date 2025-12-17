from adminportal.models import UserModuleProvision

def user_permissions(request):
    """Add user permission context to all templates"""
    if request.user.is_authenticated:
        is_admin = request.user.is_superuser
        
        if is_admin:
            allowed_modules = []  # Admin sees all
        else:
            try:
                provisions = UserModuleProvision.objects.filter(user=request.user)
                allowed_modules = [provision.module_name for provision in provisions]
            except:
                allowed_modules = []
        
        return {
            'is_admin': is_admin,
            'allowed_modules': allowed_modules,
        }
    
    return {
        'is_admin': False,
        'allowed_modules': [],
    }