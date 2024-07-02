from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='Category Name')
    photo = models.ImageField(upload_to='category_photos/', null=True, blank=True, verbose_name='Category Photo')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
class Product(models.Model):
     name = models.CharField(max_length=255, verbose_name='Product Name')
     brand= models.CharField(max_length=255, verbose_name='brand')
     category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Category')
     description = models.TextField(blank=True, null=True, verbose_name='Product Description')
     smalldescription = models.TextField(blank=True,null=True, verbose_name='small Product Description')
     photo = models.ImageField(upload_to='product_photos/', null=True, blank=True, verbose_name='product Photo')
     price = models.IntegerField(default=0)
     quantity = models.PositiveIntegerField(default=0)

    # Additional field for dress and shoe size
     size = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='Size',
        choices=[
            ('XS', 'Extra Small'),
            ('S', 'Small'),
            ('M', 'Medium'),
            ('L', 'Large'),
            ('XL', 'Extra Large'),
          
        ],
    )

     def __str__(self):
        return self.name

     def save(self, *args, **kwargs):
        # Check if the category is one of the specified categories
        kurthi_kurtha_chudithar_categories = ['Kurthi', 'Kurtha', 'Chudithar']
        if self.category.name in kurthi_kurtha_chudithar_categories:
            # If the category is one of the specified categories, allow saving the size
            super().save(*args, **kwargs)
        else:
            # If the category is not one of the specified categories, set size to None before saving
            self.size = None
            super().save(*args, **kwargs)


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.user.username})"


class Order(models.Model):
    
    name=models.CharField(max_length=90)
    email=models.CharField(max_length=111)
    address=models.CharField(max_length=111)
    city=models.CharField(max_length=111)
    state=models.CharField(max_length=111)
    zip_code=models.CharField(max_length=111)
    phone=models.CharField(max_length=15)
    payment_method_choices = [
        ('COD', 'Cash on Delivery'),
       
        ('card', 'Credit/Debit Card')
    ]
    payment_method = models.CharField(max_length=10, choices=payment_method_choices)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fullname












