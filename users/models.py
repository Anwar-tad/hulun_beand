from django.db import models
from django.contrib.auth.models import User
from PIL import Image
#Category model
class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories" # በአድሚን ገጽ ላይ "Categorys" እንዳይል
    def __str__(self):
      return self.name
# Product Model
# -# (Keep your other models like Category and Profile as they are)

class Product(models.Model):
    CONDITION_CHOICES = [
        ('New', 'አዲስ (Brand New)'),
        ('Used', 'ያገለገለ (Used)'),
        ('Refurbished', 'የታደሰ (Refurbished)'),
    ]

    name = models.CharField(max_length=200, verbose_name="የእቃው ስም")
    description = models.TextField(verbose_name="ዝርዝር መግለጫ")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ዋጋ (በብር)")
  
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=False, verbose_name="ምድብ")
    brand = models.CharField(max_length=100, blank=True, verbose_name="ዓይነት (Brand)")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, blank=True, verbose_name="ሁኔታ (Condition)")
    location = models.CharField(max_length=200, blank=True, verbose_name="የሚገኝበት ቦታ")
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ሻጭ")
    created_at = models.DateTimeField(auto_now_add=True)

    # These are the fields causing the error. Let's make sure they are perfect.
    likes = models.ManyToManyField(User, related_name='liked_products', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_products', blank=True)

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()

    def __str__(self):
        return self.name
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"
class Profile(models.Model):
  
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
      # ---  img = Image.open(self.profile_picture.path)
      #  if img.height > 300 or img.width > 300:
          #  output_size = (300, 300)
         #   img.thumbnail(output_size)
          #  img.save(self.profile_picture.path)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(default='default_avatar.png', upload_to='profile_pics/')
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
        
class Conversation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='conversations')
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        participant_names = ", ".join([user.username for user in self.participants.all()])
        return f'Conversation about "{self.product.name}" between {participant_names}'

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'Message from {self.sender.username} at {self.timestamp.strftime("%Y-%m-%d %H:%M")}'