from .models import Cart

def cart_context(request):
    cart = None
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user, is_active=True).first()
    return {'cart': cart}
