from rest_framework.permissions import IsAuthenticated

def user_permission(role_list):
    class InnerClass(IsAuthenticated):
        def has_permission(self, request, view):
            if not super(InnerClass, self).has_permission(request, view):
                return False

            return request.user.groups.filter(name__in=role_list).exists()

    return InnerClass