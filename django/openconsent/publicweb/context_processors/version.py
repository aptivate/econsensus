from publicweb import get_version

def version(request):
    '''
    A context processor to add the version number to the context.
    '''
    return {'version': '(v' + get_version() + ')'}