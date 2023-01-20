from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages
from django.db.models import Q
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.db.models import Subquery
from random import sample

from .models import User, Categories, Manufacturers, ProductListings, Watchlist, Comments, BigCategories, Orders, OrderProduct, CommentReviews

def random(ids_range):
    if len(ids_range) == 0:
        return []
    elif len(ids_range) < 3:
        return sample(ids_range, len(ids_range))
    else:
        return sample(ids_range, 3)

def cart_listing(request):
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
    return {'listings': listings, 'total': total}

def get_listing_data(request, listing_id):
    item_obj = ProductListings.objects.get(id=listing_id)
    category = item_obj.category.category_name
    cat = category[0].upper() + category[1:]
    bigcategory = item_obj.category.bigcategory_name_id.bigcategory_name
    bigcat = bigcategory[0].upper() + bigcategory[1:]
    watchlist_status = ""
    if request.user.is_authenticated:
        obj = Watchlist.objects.filter(item_id=listing_id, user_id=request.user)
        if len(obj) == 0:
            watchlist_status = 'btn-secondary'
        else:
            watchlist_status = 'btnsuccess'
    comments = Comments.objects.filter(com_item_id=listing_id)
    return {'bigcategory': bigcat, 'category': cat, 'listing': item_obj, 'comments': comments, 'watchlist_status': watchlist_status}

# Create your views here.
def index(request):
    number_of_ids_food = ProductListings.objects.exclude(quantity=0).filter(category__bigcategory_name_id__bigcategory_name="Food").values('id')
    ids_food = [item['id'] for item in number_of_ids_food]
    number_of_ids_care = ProductListings.objects.exclude(quantity=0).filter(category__bigcategory_name_id__bigcategory_name="PersonalCare").values('id')
    ids_care = [item['id'] for item in number_of_ids_care]
    number_of_ids_accessories = ProductListings.objects.exclude(quantity=0).filter(category__bigcategory_name_id__bigcategory_name="Accessories").values('id')
    ids_accessories = [item['id'] for item in number_of_ids_accessories]
    ids_food, ids_care, ids_accessories = random(ids_food), random(ids_care), random(ids_accessories)

    if request.user_agent.is_mobile:
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
    else:
        return render(request, "shop/index.html", {
            "listings_food": ProductListings.objects.filter(id__in=ids_food),
            "listings_care": ProductListings.objects.filter(id__in=ids_care),
            "listings_accessories": ProductListings.objects.filter(id__in=ids_accessories),
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
                "information": "Incorrect Password",
                "title": "Change Password"
            })
        elif request.POST['new_password'] != request.POST['repeat_new_password']:
            return render(request, "shop/information.html", {
                "information": "Passwords are not the same",
                "title": "Change Password"
            })
        else:
            u = User.objects.get(id=request.user.id)
            u.set_password(request.POST['new_password'])
            username = request.user.username
            u.save()
            login(request, authenticate(username=username, password=request.POST['new_password']))
            return render(request, "shop/information.html", {
                "information": "Password is successfully changed",
                "title": "Change Password"
            })
    else:
        return render(request, "shop/account.html")

def cart(request):
    func = cart_listing(request)
    listings = func['listings']
    total = func['total']
    if request.method == "POST":
        # Create order object
        if total == 0:
            return HttpResponseRedirect(reverse("cart"))
        newOrder = {'buyer_id': request.user, 'total_cost': total}
        order = Orders.objects.create(**newOrder)
        order.save()
        # Create triplets item-quantity-price
        for listing in listings:
            quantity = request.session['cart_session'][str(listing.id)]
            product_temp = ProductListings.objects.get(id=listing.id)
            product_temp.quantity -= quantity
            product_temp.save()
            try:
                obj = OrderProduct.objects.get(product_id = listing, product_quantity = quantity, product_price = listing.price)
                order.product.add(obj)
            except:
                newObject = {'product_id': listing, 'product_quantity': quantity, 'product_price': listing.price}
                obj = OrderProduct.objects.create(**newObject)
                obj.save()
                order.product.add(obj)

        request.session['cart_session'] = {}
            
        return render(request, "shop/information.html", {
                "information": "Thank You For Your Purchase!",
                "title": "Cart"
        })

    else:
        return render(request, "shop/cart.html", {
            "listings": listings,
            "total_price": total
        })

def listings(request, bigcategory):
    cat = bigcategory[0].upper() + bigcategory[1:]
    listings = ProductListings.objects.exclude(quantity=0).filter(category__bigcategory_name_id__bigcategory_name=cat)
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
    listings = ProductListings.objects.exclude(quantity=0).filter(category__category_name = cat)
    return render(request, "shop/listings.html", {
        "category": cat,
        "listings": listings
    })

def listing_view(request, bigcategory, category, listing_id):
    listing_data = get_listing_data(request, listing_id)
    for comment in listing_data['comments']:
        try:
            comment.reviews = CommentReviews.objects.get(comment_id=comment.id)
        except:
            pass
    return render(request, "shop/listing.html", {
        "category": listing_data['category'],
        "listing": listing_data['listing'],
        "comments": listing_data['comments'],
        "watchlist_status": listing_data['watchlist_status'],
        "range": {1, 2, 3, 4, 5}
    })

def update_cart(request, listing_id, action):
    if request.method == "POST":
        if request.POST['route'] == 'listing':
            listing_data = get_listing_data(request, listing_id)
            if listing_data['listing'].quantity == request.session['cart_session'][str(listing_id)]:
                return render(request, "shop/listing.html", {
                        "category": listing_data['category'],
                        "listing": listing_data['listing'],
                        "comments": listing_data['comments'],
                        "watchlist_status": listing_data['watchlist_status'],
                        "message": "Not enough quantity of product in storage"
                })

            try:
                request.session['cart_session'][str(listing_id)] += 1
            except:
                request.session['cart_session'][str(listing_id)] = 1
            request.session.modified = True

            return render(request, "shop/listing.html", {
                        "category": listing_data['category'],
                        "listing": listing_data['listing'],
                        "comments": listing_data['comments'],
                        "watchlist_status": listing_data['watchlist_status']
            })
        else:
            if request.POST['event'] == "add":
                listing_data = get_listing_data(request, listing_id)
                if listing_data['listing'].quantity == request.session['cart_session'][str(listing_id)]:
                    func = cart_listing(request)
                    return render(request, "shop/cart.html", {
                        "listings": func['listings'],
                        "total_price": func['total'],
                        "message": "Not enough quantity of product in storage"
                    })
                else:
                    request.session['cart_session'][str(listing_id)] += 1

            if request.POST['event'] == "remove":
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
    return render(request, "shop/order.html", {
        "products": products
    })

def watchlist(request):
    listings_food = ProductListings.objects.filter(category__bigcategory_name_id__bigcategory_name="Food", id__in=list(Watchlist.objects.filter(user_id=request.user).values_list('item_id', flat=True)))
    listings_care = ProductListings.objects.filter(category__bigcategory_name_id__bigcategory_name="PersonalCare", id__in=list(Watchlist.objects.filter(user_id=request.user).values_list('item_id', flat=True)))
    listings_accessories = ProductListings.objects.filter(category__bigcategory_name_id__bigcategory_name="Accessories", id__in=list(Watchlist.objects.filter(user_id=request.user).values_list('item_id', flat=True)))
    return render(request, "shop/watchlist.html", {
        "listings_food": listings_food,
        "listings_care": listings_care,
        "listings_accessories": listings_accessories
    })

def update_watchlist(request, listing_id):
    watchlist = Watchlist.objects.filter(item_id=ProductListings.objects.get(id=listing_id))

    if len(watchlist) != 0:
        watchlist = Watchlist.objects.filter(item_id=ProductListings.objects.get(id=listing_id), user_id=request.user)

        if len(watchlist) == 0:
            obj = Watchlist.objects.get(item_id=ProductListings.objects.get(id=listing_id))
            obj.user_id.add(request.user)
        else:
            obj = Watchlist.objects.get(item_id=ProductListings.objects.get(id=listing_id))
            obj.user_id.remove(request.user)
            if len(list(obj.user_id.all())) == 0:
                obj.delete()
    else:
        watchlist = {'item_id': ProductListings.objects.get(id=listing_id)}
        obj = Watchlist.objects.create(**watchlist)
        obj.save()
        obj.user_id.add(request.user)

    listing_data = get_listing_data(request, listing_id)
    return HttpResponseRedirect(reverse('listing_view', kwargs={'bigcategory': listing_data['bigcategory'], 'category': listing_data['category'], 'listing_id': listing_id}))

def add_comment(request):
    if request.method == "POST":
        comment = {'com_user_id':request.user, 
        'com_item_id':ProductListings.objects.get(id=request.POST['item']), 
        'comment':request.POST['comment'], 'rating':request.POST['rating-id']}
        listing = Comments.objects.create(**comment)
        listing.save()
    return HttpResponseRedirect(reverse("listing_view", 
    kwargs={'bigcategory': ProductListings.objects.get(id=request.POST['item']).category.bigcategory_name_id.bigcategory_name, 
    'category': ProductListings.objects.get(id=request.POST['item']).category.category_name, 
    'listing_id': request.POST['item']}))

def comment_review(request, comment_id, action):
    listing_data = get_listing_data(request, Comments.objects.get(id=comment_id).com_item_id.id)

    item_obj = CommentReviews.objects.filter(comment_id=comment_id)
    liked_user_id = item_obj.values_list('liked_user_id', flat=True)
    disliked_user_id = item_obj.values_list('disliked_user_id', flat=True)
    if item_obj.count() == 0:
        comment = {'comment_id': Comments.objects.get(id=comment_id)}
        item_obj = CommentReviews.objects.create(**comment)
        item_obj.save()

    item_obj = CommentReviews.objects.filter(comment_id=comment_id)

    if action=="up":
        if request.user.id not in list(liked_user_id):
            if request.user.id in list(disliked_user_id):
                item_obj[0].disliked_user_id.remove(request.user)
            item_obj[0].liked_user_id.add(request.user)
        else:
            item_obj[0].liked_user_id.remove(request.user)
        if list(item_obj.values_list('liked_user_id', flat=True))[0] == None and list(item_obj.values_list('disliked_user_id', flat=True))[0] == None:
            item_obj[0].delete()
    elif action=="down":
        if request.user.id not in list(disliked_user_id):
            if request.user.id in list(liked_user_id):
                item_obj[0].liked_user_id.remove(request.user)
            item_obj[0].disliked_user_id.add(request.user)
        else:
            item_obj[0].disliked_user_id.remove(request.user)
        if list(item_obj.values_list('liked_user_id', flat=True))[0] == None and list(item_obj.values_list('disliked_user_id', flat=True))[0] == None:
            item_obj[0].delete()

    return HttpResponseRedirect(reverse('listing_view', kwargs={
        "bigcategory": listing_data['bigcategory'],
        "category": listing_data['category'],
        "listing_id": listing_data['listing'].id
    }))