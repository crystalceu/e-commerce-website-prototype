from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Subquery
from random import sample

from .models import User, Categories, Manufacturers, ProductListings, Watchlist, Comments, BigCategories, Orders, OrderProduct

def random(ids_range):
    if len(ids_range) == 0:
        return []
    elif len(ids_range) < 3:
        return sample(ids_range, len(ids_range))
    else:
        return sample(ids_range, 3)

# Create your views here.
def index(request):
    number_of_ids_food = ProductListings.objects.filter(category__bigcategory_name_id__bigcategory_name="Food").values('id')
    ids_food = [item['id'] for item in number_of_ids_food]
    number_of_ids_care = ProductListings.objects.filter(category__bigcategory_name_id__bigcategory_name="PersonalCare").values('id')
    ids_care = [item['id'] for item in number_of_ids_care]
    number_of_ids_accessories = ProductListings.objects.filter(category__bigcategory_name_id__bigcategory_name="Accessories").values('id')
    ids_accessories = [item['id'] for item in number_of_ids_accessories]
    ids_food, ids_care, ids_accessories = random(ids_food), random(ids_care), random(ids_accessories)
    try:
        food_first = min(ids_food)
    except:
        food_first = 0
    
    try:
        care_first = min(ids_care)
    except:
        care_first = 0

    try:
        accessories_first = min(ids_accessories)
    except:
        accessories_first = 0
    return render(request, "shop/index.html", {
        "listings_food": ProductListings.objects.filter(id__in=ids_food),
        "listings_care": ProductListings.objects.filter(id__in=ids_care),
        "listings_accessories": ProductListings.objects.filter(id__in=ids_accessories),
        "food_range": range(0, len(ids_food)),
        "care_range": range(0, len(ids_care)),
        "accessories_range": range(0, len(ids_accessories)),
        "food_first": food_first,
        "care_first": care_first,
        "accessories_first": accessories_first
    })

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
        if not request.user.check_password(request.POST['current_password']):
            return render(request, "shop/information.html", {
                "information": "Incorrect Password"
            })
        elif request.POST['new_password'] != request.POST['repeat_new_password']:
            return render(request, "shop/information.html", {
                "information": "Passwords are not the same"
            })
        else:
            u = User.objects.get(id=request.user.id)
            u.set_password(request.POST['new_password'])
            username = request.user.username
            u.save()
            login(request, authenticate(username=username, password=request.POST['new_password']))
            return render(request, "shop/information.html", {
                "information": "Password is successfully changed"
            })
    else:
        return render(request, "shop/account.html")

def cart(request):
    try:
        ids = list(request.session['cart_session'].keys())
    except:
        request.session['cart_session'] = {}
        ids = list(request.session['cart_session'].keys())
    ids = [int(i) for i in ids]
    total = 0
    listings = ProductListings.objects.filter(id__in=ids)
    for listing in listings:
        listing.quantity = request.session['cart_session'][str(listing.id)]
        total += listing.price*listing.quantity

    if request.method == "POST":
        # Create order object
        if total == 0:
            return HttpResponseRedirect(reverse("cart"))
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
    if '_' in category:
        start, end = category.split('_')
        cat = start[0].upper() + start[1:] + ' ' + end[0].upper() + end[1:]
        print(cat)
    else:
        cat = category[0].upper() + category[1:]
    listings = ProductListings.objects.filter(category__category_name = cat)
    #print(listings)
    return render(request, "shop/listings.html", {
        "category": cat,
        "listings": listings
    })

def listing_view(request, bigcategory, category, listing_id):
    if request.method == "POST":
        try:
            request.session['cart_session'][str(listing_id)] += 1
        except:
            request.session['cart_session'][str(listing_id)] = 1
        request.session.modified = True
        cat = category[0].upper() + category[1:]
        listing = ProductListings.objects.get(id = listing_id)
        return HttpResponseRedirect(reverse("listing_view", kwargs={'bigcategory': bigcategory, 'category': category, 'listing_id': listing_id}))
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