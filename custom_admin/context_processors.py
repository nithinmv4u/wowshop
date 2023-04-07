from datetime import datetime


def my_context_processor(request):
    return {
        'site_name': 'WoWShoP',
        'copyright_year': datetime.now().year,
        'current_time': datetime.now().time,
    }