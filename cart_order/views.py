from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import TemplateView,View,RedirectView,ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import CartItem,Cart,Coupon, UsedCoupon, Order, OrderItem, ShippingAddress, RazorpayPayment
from stores.models import Product,ProductSize
from authentication.models import User
from authentication.models import Address
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from .forms import UpdateCartItemForm
from django.urls import reverse_lazy
import json
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime
from django.db import transaction
from django.db.models import Q
import random
import string
from decimal import Decimal
import razorpay
import wowshop.settings

class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'shoping_cart.html'
    login_url = 'authentication:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        cart_items = CartItem.objects.filter(user=user)
        try:
            cart= Cart.objects.get(user=user,is_active=True)
        except Cart.DoesNotExist:
            cart = None
        if cart:
            context['cart_items'] = cart_items
            context['total_price'] = cart.total_price() #total price of cart items from cartitem model
            context['cart_tax'] = cart.calculate_tax()
            context['cart_grand_total'] = cart.total_after_tax()
        return context

# ----------check total quantity of product--------------- 
class AddToCartView(LoginRequiredMixin,View):
    def post(self, request, *args, **kwargs):
        product_id = kwargs['pk']
        quantity = request.POST.get('quantity', 1)
        size_id = request.POST.get('size_id')
        print("size id: ",size_id)
        print("quantity: ",quantity)
        print(request.POST)
        if not quantity or not size_id:
            return JsonResponse({'success': False, 'error': 'Select valid Size and Quantity'})

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError('Quantity must be a positive integer')
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid quantity'})

        product_size_object = get_object_or_404(ProductSize, id=size_id)
        print(product_size_object)
        product_size= product_size_object.size
        product_object = product_size_object.product
        print(product_object)
        print(product_size)
        if quantity > product_size_object.stock:
            return JsonResponse({'success': False, 'error': 'Not enough quantity'})

        cart, created = Cart.objects.get_or_create(user=request.user, is_checked_out=False)
        print(quantity)
        cart.add_item(product_object, quantity, product_size_object)
        cart.grand_total = cart.calculate_grand_total()
        cart.save()
        print(cart.grand_total)
        return JsonResponse({'success': True})


class UpdateCartItemView(LoginRequiredMixin,View):
    def post(self, request, pk):
        print("update")
        data = json.loads(request.body)
        new_quantity = data.get('quantity')
        print(new_quantity)
        if new_quantity:
            cart_item = CartItem.objects.get(pk=pk)
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f'{cart_item.product} quantity updated to {new_quantity}')
            cart= Cart.objects.get(user=request.user,is_active=True)
            cart_item_total_price=cart_item.total_price()
            cart_total_price = cart.total_price()
            cart_tax = cart.calculate_tax()
            cart_grand_total = cart.total_after_tax()
            cart.grand_total = cart.calculate_grand_total()
            cart.save()
            data = {
                'cart_item_total_price' : cart_item_total_price,
                'cart_total_price': cart_total_price,
                'cart_tax':cart_tax,
                'cart_grand_total':cart_grand_total,
            }
            return JsonResponse(data)
        else:
            error_msg = "quantity can't be 'zero'"
            data = {'error': error_msg}
            return JsonResponse(data, status=400)
    
class RemoveFromCartView(LoginRequiredMixin,RedirectView):
    url = reverse_lazy('cart_order:cart')

    def get_redirect_url(self, *args, **kwargs):
        cart_item = CartItem.objects.filter(pk=self.kwargs.get('pk')).first()
        if cart_item:
            cart_item.delete()
            messages.success(self.request, "Item removed from cart successfully")
        cart= Cart.objects.get(user=self.request.user,is_active=True)
        cart.grand_total = cart.calculate_grand_total()
        cart.save()
        return super().get_redirect_url(*args, **kwargs)
    
class CheckoutView(LoginRequiredMixin,TemplateView):
    template_name="checkout.html"
    login_url = 'authentication:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            cart= Cart.objects.get(user=user,is_active=True)
        except Cart.DoesNotExist:
            cart = None
        # cart = Cart.objects.get(user=user)
        if cart:
            addresses = Address.objects.filter(user=user)
            price=cart.total_after_tax() #total price of cart from cart model
            coupon = cart.coupon
            discount = cart.discount
            cart.grand_total = cart.calculate_grand_total(coupon)
            context['total_price'] = price
            context['user'] = user
            context['addresses'] = addresses
            context['no_cart'] = True
            context['coupon'] = coupon
            context['discount'] = discount
            context['grand_total'] = cart.grand_total
        else:
            context['no_cart'] = False
        return context
    
class CouponAdminView(ListView):
    template_name = 'coupon_list.html'
    paginate_by = 6

    def get(self, request):
        coupons = Coupon.objects.all()
        context = {'coupons': coupons}
        return render(request, self.template_name, context)

    def post(self, request):
        if 'coupon_id' in request.POST:
            print("if")
            coupon_id = request.POST.get('coupon_id')
            coupon = Coupon.objects.get(pk=coupon_id)
            coupon.toggle_enabled()
            message = f"Coupon {coupon.code} {'Enabled' if coupon.active else 'Disabled'} successfully!"
        else:
            print("else")
            code = request.POST.get('code')
            discount = request.POST.get('discount')
            valid_from = timezone.now()
            valid_to_str = request.POST.get('valid_to')
            # to avoid RuntimeWarning: DateTimeField Coupon.valid_to received a naive datetime
            valid_to = timezone.datetime.strptime(valid_to_str, '%Y-%m-%dT%H:%M')
            # valid_to = timezone.make_aware(valid_to, timezone.get_current_timezone())
            active = request.POST.get('active', False)
            coupon = Coupon.create(code, discount, valid_from, valid_to, active)
            message = f'Coupon {coupon.code} created successfully!'

        coupons = Coupon.objects.all()
        context = {'coupons': coupons, 'message': message}
        return render(request, self.template_name, context)

class ApplyCouponView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        code = request.POST.get('coupon_code')
        print(code)
        try:
            with transaction.atomic():
                coupon = Coupon.objects.select_for_update().get(
                    code=code,
                    active=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now(),
                    is_single_use=True
                )
                cart = Cart.objects.filter(
                    user=request.user,
                    is_active=True,
                    is_checked_out=False
                ).first()
                if not cart:
                    return JsonResponse({'error': 'Cart not found..!'})
                if cart.coupon:
                    return JsonResponse({'error': 'Coupon already applied..!'})
                # Check if the user has already used this coupon
                if UsedCoupon.objects.filter(user=request.user, coupon=coupon).exists():
                    return JsonResponse({'error': 'Coupon already used..!'})
                print("all pass")
                sub_total = cart.total_after_tax()
                discount_amount = coupon.discount_amount(sub_total)
                cart.coupon = coupon
                cart.discount = discount_amount
                grand_total = cart.calculate_grand_total(coupon)
                cart.grand_total = grand_total
                cart.save()
                # coupon.toggle_enabled()  # Toggle the is_single_use flag
                # Create a UsedCoupon object to record that the user has used this coupon
                UsedCoupon.objects.create(user=request.user, coupon=coupon)
                context = {
                    'grand_total' : f'₹ {grand_total}',
                    'discount_amount' : f'Discount: ₹ {discount_amount}',
                    'code' : code,
                    'success' : 'Coupon '+ code +' Applied'
                }

                return JsonResponse(context)
        except Coupon.DoesNotExist:
            return JsonResponse({'error': 'Invalid coupon code..!'})

class RemoveCouponView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                cart = Cart.objects.filter(
                    user=request.user,
                    is_active=True,
                    is_checked_out=False
                ).first()
                if not cart:
                    return JsonResponse({'error': 'Cart not found'})
                if not cart.coupon:
                    return JsonResponse({'error': 'No coupon applied'})
                coupon = cart.coupon
                cart.coupon = None
                cart.discount = 0
                cart.grand_total = cart.calculate_grand_total()
                cart.save()
                # Toggle the is_single_use flag of the coupon
                # coupon.toggle_enabled()
                UsedCoupon.objects.filter(user=request.user, coupon=coupon).delete()
                context = {
                    'grand_total': '₹ ' + str(cart.calculate_grand_total()),
                    'discount_amount': '',
                    'code': '',
                    'success': 'Coupon removed'
                }
                return JsonResponse(context)
        except Exception as e:
            return JsonResponse({'error': str(e)})


class OrderCreateView(View):

    def generate_order_number(self):
        now = datetime.now()
        timestamp = int(now.timestamp())
        random_number = random.randint(1000, 9999)
        order_number = f'{timestamp}{random_number}'
        return order_number

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        print('request: ',request.POST)
        # Retrieve shipping address information from the form
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        h_name = request.POST.get('h_name')
        email = request.POST.get('email')
        street_address = request.POST.get('street_address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        order_note = request.POST.get('order_note')

        # Create the shipping address object
        shipping_address = ShippingAddress(
            first_name=first_name,
            last_name=last_name,
            h_name=h_name,
            email=email,
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone,
            order_note=order_note,
        )
        # shipping_address.save()

        # Create the order object
        # get_grand_total = Cart.objects.filter(user=self.request.user).values_list('grand_total', flat=True).first()
        latest_cart = Cart.objects.filter(user=request.user, is_active=True).latest('created_at')
        get_grand_total = latest_cart.grand_total
        print(get_grand_total)
        razorpay_grand_total = int(get_grand_total*100)
        try:
            # used_coupon = UsedCoupon.objects.get(user=self.request.user)
            # here used Q to get used coupon matching current user and latest cart, that will be uneque, else filter must have been used. but it is mandatory to have only a coupon at a cart fro a user
            used_coupon = UsedCoupon.objects.get(Q(user=self.request.user) & Q(coupon=latest_cart.coupon))
        except UsedCoupon.DoesNotExist:
            used_coupon = None
        order = Order(
            order_number=self.generate_order_number(),  # Implement your own function to generate unique order number
            grand_total=get_grand_total,  # Implement your own function to calculate grand total
            customer=request.user,
            payment_status='pending',  # Set initial payment status as pending
            used_coupon=used_coupon
        )
        order.save()

        # Create the order items
        #         #cart = Cart.objects.filter(user=self.request.user) # returns Cart Object to have methods also associated with it
        cart_items = CartItem.objects.filter(user=self.request.user) # returns QuerySet Object not a Cart object
        print(cart_items)
        for item in cart_items:  
            order_item = OrderItem(
                quantity=item.quantity,
                size = item.size,
                total_price=item.total_price(),
                product=item.product,
                order=order,
            )
            order_item.save()

        shipping_address.order = order
        shipping_address.save()

        # checkout the cart
        cart = Cart.objects.get(user=self.request.user)
        cart.is_checked_out = True  
        # Redirect to the order summary page

        #razorpay
        client = razorpay.Client(auth=(wowshop.settings.RAZORPAY_API_KEY, wowshop.settings.RAZORPAY_API_SECRET))

        data = { "amount": razorpay_grand_total, "currency": "INR", "receipt": "order_rcptid_11" }
        payment = client.order.create(data=data)
        razorpay_order_id = payment['id']
        print(payment)
        order.razorpay_order_id=razorpay_order_id
        order.save()
        return redirect('cart_order:order_summary', order_id=order.id)
    
class OrderSummaryView(TemplateView):
    template_name = 'order_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = Order.objects.latest('id')
        print(order.grand_total)
        context['order'] = order
        context['order_items'] = OrderItem.objects.filter(order=order)
        context['shipping_address'] = ShippingAddress.objects.filter(order=order).first()
        
        # Fetch the Razorpay order details
        client = razorpay.Client(auth=(wowshop.settings.RAZORPAY_API_KEY, wowshop.settings.RAZORPAY_API_SECRET))
        razorpay_order_id = order.razorpay_order_id
        razorpay_order = client.order.fetch(razorpay_order_id)

        # Extract the amount from the Razorpay order
        razorpay_amount = razorpay_order['amount']
        context['razorpay_amount'] = razorpay_amount
        return context

class OrderConfirmationView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_confirmation.html'
    context_object_name = 'order'
    login_url = reverse_lazy('authentication:login')

    def get(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        try:
            order = Order.objects.get(id=order_id, customer=request.user)
            order_items = OrderItem.objects.filter(order=order)
            shipping_address = ShippingAddress.objects.get(order=order)
            # Clear the cart
            order.payment_method = 'COD'
            cart = Cart.objects.get(user=request.user, is_checked_out=False)
            cart_items = cart.items.all()
            cart_items.delete()
            cart.delete()
            return self.render_to_response({
                'order': order,
                'order_items':order_items,
                'shipping_address':shipping_address,
                })
        except Order.DoesNotExist:
            return redirect('home')
        
class RazorpayConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'order_confirmation.html'
    login_url = reverse_lazy('authentication:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = kwargs.get('order_id')
        print("get order id: ",order_id)
        order = Order.objects.get(id=order_id, customer=self.request.user)
        order_items = OrderItem.objects.filter(order=order)
        shipping_address = ShippingAddress.objects.get(order=order)
        payment = RazorpayPayment.objects.get(payment_id=order.razorpay_order_id)
        context['order'] = order
        context['order_items'] = order_items
        context['shipping_address'] = shipping_address
        context['payment'] = payment
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('order_id')
        print(order_id)
        # Fetch the razorpay_payment_id and razorpay_order_id
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_signature = request.POST.get('razorpay_signature')
        razorpay_amount = request.POST.get('amount')

        print("razorpay_payment_id", razorpay_payment_id)
        print("razorpay_order_id", razorpay_order_id)
        print("razorpay_signature", razorpay_signature)
        print("razorpay_amount", razorpay_amount)

        # Verify the signature
        client = razorpay.Client(auth=("rzp_test_i1bO74aj4OXMfL", "pUoNuwHwlmI0WPiCt9dquqAf"))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }
        try:
            resp = client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            # If signature verification fails, redirect to error page
            return HttpResponseBadRequest('Invalid Signature')

        # Fetch the order object and update its payment status
        order = Order.objects.get(id=order_id, customer=request.user)
        order_items = OrderItem.objects.filter(order=order)
        shipping_address = ShippingAddress.objects.get(order=order)

        # Update order payment details
        order.payment_method = 'RAZORPAY'
        order.razorpay_order_id = razorpay_payment_id
        order.payment_status = 'Completed'
        order.save()

        # create razorpay payment record
        payment = RazorpayPayment.objects.create(
            payment_id=razorpay_payment_id,
            order_id=razorpay_order_id,
            signature=razorpay_signature,
            amount=order.grand_total,
            status='SUCCESS',
        )

        # Clear the cart
        cart = Cart.objects.get(user=request.user, is_checked_out=False)
        cart_items = cart.items.all()
        cart_items.delete()
        cart.delete()

        print("payment: ",payment)
        print("order: ",order)
        print("order_items: ",order_items)
        print("shipping_address: ",shipping_address)
        context = {
            'payment': payment,
            'order': order,
            'order_items': order_items,
            'shipping_address': shipping_address,
        }
        print("context: ", context)
        print(order.order_number)
        # Render the order confirmation page with the order details
        return render(request, self.template_name, context)
        # return self.render_to_response(context)

class OrderHistoryView(LoginRequiredMixin, ListView):
    template_name = 'order_history.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.filter(customer=self.request.user).order_by('-date_ordered')
        for order in queryset:
            order_items = OrderItem.objects.filter(order=order)
            shipping_address = ShippingAddress.objects.get(order=order)
            try:
                payment = RazorpayPayment.objects.get(payment_id=order.razorpay_order_id)
            except:
                payment = None
            order.order_items = order_items
            order.shipping_address = shipping_address
            order.payment = payment
        return queryset
    




# class OrderCreateView(LoginRequiredMixin, CreateView):
#     model = Order
#     fields = []
#     success_url = reverse_lazy('order_summary')
#     template_name = 'order_summary.html'

#     def generate_order_number(self):
#         now = datetime.now()
#         timestamp = int(now.timestamp())
#         random_number = random.randint(1000, 9999)
#         order_number = f'{timestamp}{random_number}'
#         return order_number
     
#     @transaction.atomic
#     def form_valid(self, form):
#         #cart = Cart.objects.filter(user=self.request.user) # returns Cart Object to have methods also associated with it
#         cart_items = CartItem.objects.filter(user=self.request.user) # returns QuerySet Object not a Cart object
#         customer = self.request.user
#         # customer = self.request.get_user()
#         shipping_address = ShippingAddress(
#             first_name=self.request.POST['firstName'],
#             last_name=self.request.POST['lastName'],
#             h_name=self.request.POST['h_name'],
#             email=self.request.POST['email'],
#             street_address=self.request.POST['street_address'],
#             city=self.request.POST['city'],
#             state=self.request.POST['state'],
#             zip_code=self.request.POST['zip_code'],
#             phone=self.request.POST['phone'],
#             order_note = self.request.POST['orderNote'],
#         )
#         #shipping_address.save()
#         grand_total = Cart.objects.filter(user=self.request.user).values_list('grand_total', flat=True).first()
#         print(grand_total)
#         order = Order(
#             order_number=self.generate_order_number(),
#             grand_total=grand_total,
#             customer=customer,
#             payment_status='pending',
#         )

#         # order = Order()
#         # order.grand_total=grand_total
#         # order.customer=customer
#         # order.payment_status='pending'
#         # order.order_number=self.generate_order_number()
        
#         print(order.grand_total)
#         order.save()
#         for cart_item in cart_items:
#             order_item = OrderItem(
#                 quantity= cart_item.quantity,
#                 price=cart_item.total_price(),
#                 product=cart_item.product,
#                 order=order,
#             )
#             order_item.save()
#         shipping_address.order = order
#         shipping_address.save()
#         # add code to set is_checked_out field of cart set to True and create a cookie with time out to store order summary if user accidently closes tab.
#         return super().form_valid(form)
    
#     def form_invalid(self, form):
#         messages.error(self.request, 'There was an error processing your order. Please try again.')
#         return redirect('checkout')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         order = Order.objects.latest('id')
#         context['order'] = order
#         context['order_items'] = OrderItem.objects.filter(order=order)
#         context['shipping_address'] = ShippingAddress.objects.filter(order=order).first()
#         return context

    

# class UpdateCartItemView(LoginRequiredMixin, View):
#     def post(self, request, *args, **kwargs):
#         cart_item = CartItem.objects.get(pk=self.kwargs['pk'], cart__user=request.user, cart__is_checked_out=False)
#         quantity = int(request.POST.get('quantity', 1))
#         if quantity <= 0:
#             cart_item.delete()
#         else:
#             cart_item.quantity = quantity
#             cart_item.save()
#         cart = Cart.objects.get(user=request.user, is_checked_out=False)
#         total_price = cart.get_total_price()
#         cart_item_total_price = cart_item.get_total_price()
#         return JsonResponse({'success': True, 'cart_total_price': total_price, 'cart_item_total_price': cart_item_total_price})