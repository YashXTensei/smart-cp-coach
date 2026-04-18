from django.contrib.auth.models import User
from django.db import models 

class Platform(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Topic(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Problem(models.Model):
    title = models.CharField(max_length=255)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    problem_code = models.CharField(max_length=100) 

    DIFFICULTY_CHOICES = [
    ('easy', 'Easy'),
    ('medium', 'Medium'),
    ('hard', 'Hard'),
    ]
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES
    )
    rating = models.IntegerField(null=True, blank=True)

    link = models.URLField()

    topics = models.ManyToManyField(Topic, related_name='problems')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('platform', 'problem_code')

    def __str__(self):
        return f"{self.title} ({self.platform})"
    

class UserProblem(models.Model):
    STATUS_CHOICES = [
        ('unsolved', 'Unsolved'),
        ('solved', 'Solved'),
        ('revision', 'Revision'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_problems')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unsolved')
    is_favorite = models.BooleanField(default=False)

    # CF se fetch hone wala actual wrong attempt count (WA + TLE + RE etc.)
    wrong_attempts = models.IntegerField(default=0)

    last_practiced = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    # Auto-calculated priority score for review queue (higher = review karo pehle)
    review_priority = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'problem')

    def __str__(self):
        return f"{self.user} - {self.problem}"
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    cf_handle = models.CharField(max_length=100, blank=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    last_cf_submission_id = models.BigIntegerField(null=True, blank=True)  
    cf_rating = models.IntegerField(null=True, blank=True)
    cf_rank = models.CharField(max_length=50, blank=True)
    verification_problem = models.CharField(max_length=20, blank=True)
    verification_expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.cf_handle or 'No CF Handle'}"