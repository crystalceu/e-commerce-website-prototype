from django.contrib import admin
from .models import User, Categories, Manufacturers, ProductListings, Watchlist, Comments, BigCategories, Orders, OrderProduct

# Register your models here.
admin.site.register(User)
admin.site.register(Categories)
admin.site.register(Manufacturers)
admin.site.register(ProductListings)
admin.site.register(Watchlist)
admin.site.register(Comments)
admin.site.register(BigCategories)
admin.site.register(Orders)
admin.site.register(OrderProduct)