from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    pass

class BigCategories(models.Model):
    id = models.AutoField(primary_key=True)
    bigcategory_name = models.CharField(max_length = 64)

class Categories(models.Model):
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length = 64)
    bigcategory_name_id = models.ForeignKey(BigCategories, on_delete=models.CASCADE, related_name="bigcategory_name_id")

class Manufacturers(models.Model):
    id = models.AutoField(primary_key=True)
    manufacturer_name = models.CharField(max_length = 64)
    location_name = models.CharField(max_length = 64)

class ProductListings(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length = 48, unique=True)
    description = models.CharField(max_length = 256)
    image = models.ImageField(upload_to = 'product-img/')
    price = models.IntegerField()
    manufacturer = models.ForeignKey(Manufacturers, on_delete=models.CASCADE, related_name="manufacturer")
    category = models.ForeignKey(Categories, on_delete=models.CASCADE, related_name="category")
    quantity = models.IntegerField()

class OrderProduct(models.Model):
    id = models.AutoField(primary_key=True)
    product_id = models.ForeignKey(ProductListings, on_delete=models.CASCADE, related_name="buyer_id")
    product_quantity = models.IntegerField()
    product_price = models.IntegerField()

    @classmethod
    def create(cls, **dinfo):
        product = cls(product_id=dinfo[0], product_quantity=dinfo[1], product_price=dinfo[2])
        return product

class Orders(models.Model):
    id = models.AutoField(primary_key=True)
    buyer_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer_id")
    product = models.ManyToManyField(OrderProduct, blank=True, related_name="product")
    total_cost = models.IntegerField()
    order_time = models.DateTimeField(default=timezone.now)

    @classmethod
    def create(cls, **dinfo):
        order = cls(buyer_id=dinfo[0], total_cost=dinfo[2])
        return order

class Watchlist(models.Model):
    id = models.AutoField(primary_key=True)
    item_id = models.ForeignKey(ProductListings, on_delete=models.CASCADE, related_name="item_id")
    user_id = models.ManyToManyField(User, blank=True, related_name="user_id")

class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    com_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="com_user_id")
    com_item_id = models.ForeignKey(ProductListings, on_delete=models.CASCADE, related_name="com_item_id")
    comment = models.CharField(max_length = 256)
    time = models.DateTimeField(default=timezone.now)