from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum

# You can extend the User model if needed, but for now we'll use Django's built-in User model
# The built-in User model includes:
# - username
# - password
# - email
# - first_name
# - last_name
# - is_staff (for admin access)
# - is_active
# - is_superuser

# If you need additional fields, you can create a profile model:
class UserProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ], default='staff')
    phone_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Church(models.Model):
    name = models.CharField(max_length=200)
    host_pastor = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.host_pastor}"

class Participant(models.Model):
    MINISTRY_CHOICES = [
        ('guitarist', 'Guitarist'),
        ('drummer', 'Drummer'),
        ('keyboard', 'Keyboard'),
        ('bassist', 'Bassist'),
    ]
    
    STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]
    
    CATEGORY_CHOICES = [
        ('youth', 'Youth'),
        ('pastor', 'Pastor'),
    ]
    
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    type_of_ministry = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    category = models.CharField(max_length=100, blank=True, null=True)
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    color = models.CharField(max_length=7, default='#007bff', help_text="Color code for participant identification")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Registration fee is now manually entered by user
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.category or 'Custom'}"

class Finance(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    EXPENSE_CATEGORIES = [
        ('food', 'Food & Beverages'),
        ('transportation', 'Transportation'),
        ('accommodation', 'Accommodation'),
        ('materials', 'Materials & Supplies'),
        ('entertainment', 'Entertainment'),
        ('utilities', 'Utilities'),
        ('other', 'Other'),
    ]
    
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    expense_category = models.CharField(max_length=20, choices=EXPENSE_CATEGORIES, null=True, blank=True)
    recorded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type.title()}: {self.description} - ₱{self.amount}"

class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('vs_sports', 'VS Sports Game'),
        ('survival', 'Survival Game'),
    ]
    
    GAME_CHOICES = [
        ('basketball', 'Basketball'),
        ('volleyball', 'Volleyball'),
        ('soccer', 'Soccer'),
        ('badminton', 'Badminton'),
        ('obstacle_challenge', 'Obstacle Challenge'),
        ('team_survival', 'Team Survival'),
        ('scavenger_hunt', 'Scavenger Hunt'),
        ('relay_race', 'Relay Race'),
    ]
    
    name = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    game_type = models.CharField(max_length=50, choices=GAME_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.game_type.title()} - {self.name}"

class VSGameResult(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    church_a = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='vs_games_as_team_a')
    church_b = models.ForeignKey(Church, on_delete=models.CASCADE, related_name='vs_games_as_team_b')
    church_a_score = models.PositiveIntegerField(default=0)
    church_b_score = models.PositiveIntegerField(default=0)
    winner = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True, related_name='vs_wins')
    display_in_scoring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.church_a.name} VS {self.church_b.name} - {self.church_a_score}:{self.church_b_score}"

class SurvivalGameResult(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    church = models.ForeignKey(Church, on_delete=models.CASCADE)
    points_earned = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(null=True, blank=True)
    display_in_scoring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_demerits(self):
        return self.demerits.aggregate(total=models.Sum('points'))['total'] or 0
    
    @property
    def total_merits(self):
        return self.merits.aggregate(total=models.Sum('points'))['total'] or 0
    
    @property
    def final_score(self):
        return (self.points_earned + self.total_merits) - self.total_demerits
    
    def __str__(self):
        return f"{self.church.name} - {self.points_earned} points"

class Demerit(models.Model):
    VIOLATION_TYPES = [
        ('late', 'Late Arrival'),
        ('misconduct', 'Misconduct'),
        ('rule_violation', 'Rule Violation'),
        ('unsportsmanlike', 'Unsportsmanlike Behavior'),
        ('equipment', 'Equipment Violation'),
        ('other', 'Other'),
    ]
    
    survival_result = models.ForeignKey(SurvivalGameResult, on_delete=models.CASCADE, related_name='demerits')
    points = models.PositiveIntegerField(default=0)
    violation_type = models.CharField(max_length=20, choices=VIOLATION_TYPES)
    reason = models.TextField(blank=True, help_text="Optional reason for the violation")
    recorded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.survival_result.church.name} - {self.points} demerits ({self.get_violation_type_display()})"

class Merit(models.Model):
    MERIT_TYPES = [
        ('excellent_performance', 'Excellent Performance'),
        ('teamwork', 'Teamwork'),
        ('leadership', 'Leadership'),
        ('sportsmanship', 'Sportsmanship'),
        ('creativity', 'Creativity'),
        ('effort', 'Effort'),
        ('improvement', 'Improvement'),
        ('other', 'Other'),
    ]
    
    survival_result = models.ForeignKey(SurvivalGameResult, on_delete=models.CASCADE, related_name='merits')
    points = models.PositiveIntegerField(default=0)
    merit_type = models.CharField(max_length=25, choices=MERIT_TYPES)
    reason = models.TextField(blank=True, help_text="Optional reason for merit")
    recorded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.survival_result.church.name} - {self.points} merits ({self.get_merit_type_display()})"
