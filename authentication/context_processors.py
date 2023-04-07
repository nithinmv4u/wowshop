from datetime import datetime
from stores.models import Product

def combined_context_processor(request):
    return {**my_context_processor(request), **context_login(request),}

def my_context_processor(request):
    return {
        'site_name': 'WoWShoP',
        'copyright_year': datetime.now().year,
        'current_time': datetime.now().time,
    }

def context_login(request):
    return{
        'login_form_data' : request.POST.dict()
    }


# def products(request):
#     return {'products': Product.objects.all()}