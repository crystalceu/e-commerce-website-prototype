from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Subquery

from .models import User, Categories, Manufacturers, ProductListings, Watchlist, Comments, BigCategories, Orders, OrderProduct

# Create your views here.
def index(request):
    return render(request, "shop/index.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            request.session['cart_session'] = {}
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "shop/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "shop/login.html")

def logout_view(request):
    try:
        del request.session['cart_session']
    except KeyError:
        pass
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "shop/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "shop/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "shop/register.html")

def account(request):
    if request.method == "POST":
        if check_password(request.user.password, request.POST['current_password']):
            print("Incorrect Password")
        elif request.POST['new_password'] != request.POST['repeat_new_password']:
            print("Passwords are not the same")
        else:
            print(make_password(request.POST['new_password'], salt=None, hasher='default'))
            request.user.password = make_password(request.POST['new_password'], salt=None, hasher='default')
            print("Password has been changed")
        return HttpResponseRedirect(reverse("account"))
    else:
        return render(request, "shop/account.html")

def cart(request):
    ids = list(request.session['cart_session'].keys())
    ids = [int(i) for i in ids]
    total = 0
    listings = ProductListings.objects.filter(id__in=ids)
    for listing in listings:
        listing.quantity = request.session['cart_session'][str(listing.id)]
        total += listing.price*listing.quantity

    if request.method == "POST":
        # Create order object
        newOrder = {}
        newOrder = {'buyer_id': request.user, 'total_cost': total}
        order = Orders.objects.create(**newOrder)
        order.save()
        # Create triplets item-quantity-price
        for listing in listings:
            quantity = request.session['cart_session'][str(listing.id)]
            try:
                obj = OrderProduct.objects.get(product_id = listing, product_quantity = quantity, product_price = listing.price)
                order.product.add(obj)
            except:
                newObject = {'product_id': listing, 'product_quantity': quantity, 'product_price': listing.price}
                obj = OrderProduct.objects.create(**newObject)
                obj.save()
                order.product.add(obj)
        request.session['cart_session'] = {}
            
        return render(request, "shop/success.html")
    else:
        return render(request, "shop/cart.html", {
            "listings": listings,
            "total_price": total
        })

def listings(request, bigcategory):
    cat = bigcategory[0].upper() + bigcategory[1:]
    listings = ProductListings.objects.filter(category__bigcategory_name_id__bigcategory_name = cat)
    return render(request, "shop/listings.html", {
        "category":  cat,
        "listings": listings
    })

def listing(request, bigcategory, category):
    cat = category[0].upper() + category[1:]
    listings = ProductListings.objects.filter(category__category_name = cat)
    #print(listings)
    return render(request, "shop/listings.html", {
        "listings": listings
    })

def listing_view(request, bigcategory, category, listing_id):
    if request.method == "POST":
        try:
            request.session['cart_session'][str(listing_id)] += 1
        except:
            request.session['cart_session'][str(listing_id)] = 1
        request.session.modified = True
        print(request.session['cart_session'])
        print(list(request.session['cart_session'].keys()))
        cat = category[0].upper() + category[1:]
        listing = ProductListings.objects.get(id = listing_id)
        return render(request, "shop/listing.html", {
            "category": cat,
            "listing": listing
        })
    else:
        cat = category[0].upper() + category[1:]
        listing = ProductListings.objects.get(id = listing_id)
        return render(request, "shop/listing.html", {
            "category": cat,
            "listing": listing
        })

def update_cart(request, listing_id, action):
    if request.method == "POST":
        if action == "add":
            request.session['cart_session'][str(listing_id)] += 1
        if action == "remove":
            if request.session['cart_session'][str(listing_id)] == 1:
                request.session['cart_session'].pop(str(listing_id), None)
            else:
                request.session['cart_session'][str(listing_id)] -= 1
        request.session.modified = True

        return HttpResponseRedirect(reverse("cart"))

def orders_view(request):
    listings = Orders.objects.filter(buyer_id = request.user)
    return render(request, "shop/orders.html", {
        "listings": listings
})

def order_view(request, order_id):
    products = Orders.objects.get(id = order_id)
    print(products)
    print(products.product)
    print(products.product.all)
    return render(request, "shop/order.html", {
        "products": products
    })