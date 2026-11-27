from .permissions import es_administrador, es_tutor


def roles_y_perfil(request):
    usuario = request.user
    if not usuario.is_authenticated:
        return {'perfil': None, 'es_admin': False, 'es_tutor': False}
    try:
        perfil = usuario.perfil
    except Exception:
        perfil = None
    return {
        'perfil': perfil,
        'es_admin': es_administrador(usuario),
        'es_tutor': es_tutor(usuario),
    }
