from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import uuid

class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField(unique=True, max_length=150)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1

            while Account.objects.filter(slug=unique_slug).exclude(id=self.id).exists():
                unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"  # Use UUID for uniqueness

            self.slug = unique_slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    
    
class Transaction(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='receiver')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField()    
    def __str__(self):
        return f'{self.sender} sent {self.amount} to {self.receiver}'
    class Meta:
        ordering = ['-date']
    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now()
        
        super().save(*args, **kwargs)
    
    
