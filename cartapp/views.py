from django.conf import settings
from django.core.checks import messages
from django.shortcuts import render,redirect,get_object_or_404
from shopapp.models import Product
from . models import Cart,CartItem
from django.core.exceptions import ObjectDoesNotExist
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart
def add_cart(request,product_id):
    product=Product.objects.get(id=product_id)
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart=Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save();
    try:
        cart_item=CartItem.objects.get(product=product,cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity +=1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item=CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        cart_item.save()
    return redirect('cartapp:cart_detail')
def cart_detail(request,total=0,counter=0,cart_items=None):
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart,active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.price * cart_item.quantity)
            counter +=cart_item.quantity
    except ObjectDoesNotExist:
        pass
    return render(request,'cart.html',dict(cart_items=cart_items,total  =total,counter = counter))

def cart_remove(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=CartItem.objects.get(product=product,cart=cart)
    if cart_item.quantity>1:
        cart_item.quantity -=1
        cart_item.save()
    else:
        cart_item.delete()
    return  redirect('cartapp:cart_detail')
def full_remove(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(Product,id=product_id)
    cart_item=CartItem.objects.get(product=product,cart=cart)
    cart_item.delete()
    return  redirect('cartapp:cart_detail')


def my_view(request):
    # Correct usage without any arguments
    return redirect(reverse('make_payment'))


def make_payment(request):
    if request.method == 'POST':
        # Retrieve payment information from the form
        token = request.POST['stripeToken']
        amount = 1000  # Sample amount in cents (e.g., $10.00)

        try:
            # Create a charge using the Stripe API
            charge = stripe.Charge.create(
                amount=amount,
                currency='usd',
                description='Example charge',
                source=token,
            )

            # Payment successful, update order status, send confirmation email, etc.
            # Replace this with your actual logic

            messages.success(request, 'Payment successful!')
            return redirect('order_success')  # Redirect to a success page

        except stripe.error.CardError as e:
            # Payment failed, handle the error
            error_msg = e.error.message
            messages.error(request, f'Payment failed: {error_msg}')
            return redirect('payment_failed')  # Redirect to a failure page
    return render(request, 'payment.html')