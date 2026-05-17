from django.db import models

from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):

    CATEGORY_CHOICES = [
        ('food', 'Food'),
        ('transport', 'Transport'),
        ('study', 'Study'),
        ('shopping', 'Shopping'),
        ('bills', 'Bills'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    expense_date = models.DateField(null=True)  # stores local date explicitly

    def __str__(self):
        return f"{self.category} - {self.amount}"
    
    
    
class BudgetCycle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    current_day_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)  

    limit_last_updated = models.DateField(null=True, blank=True)  


    def __str__(self):
        return f"{self.user.username} - {self.total_amount}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    image = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return self.user.username