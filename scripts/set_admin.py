from apps.accounts.models import User

try:
    u = User.objects.get(username='yusuf')
    print('found', u.username, u.role, u.is_staff, u.is_superuser)
    u.role = 'ADMIN'
    u.is_staff = True
    u.is_superuser = True
    u.save()
    print('updated', u.username, u.role, u.is_staff, u.is_superuser)
except Exception as e:
    print('ERROR', e)
