from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings

# Mentorship categories
class MentorshipCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Mentor Application
class MentorApplication(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="mentor_application")
    applied_on = models.DateTimeField(default=timezone.now)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Mentor application by {self.user.username}"

# One-to-One Mentorship
class OneOnOneMentorship(models.Model):
    mentor = models.ForeignKey(User, related_name='mentorship_mentor', on_delete=models.CASCADE)
    mentee = models.ForeignKey(User, related_name='mentorship_mentee', on_delete=models.CASCADE)
    category = models.ForeignKey(MentorshipCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.mentor.username} mentors {self.mentee.username} in {self.category.name}"

# Group Mentorship
class GroupMentorship(models.Model):
    name = models.CharField(max_length=255)
    mentor = models.ForeignKey(User, related_name='group_mentorship_mentor', on_delete=models.CASCADE)
    category = models.ForeignKey(MentorshipCategory, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='group_mentorship_members')
    points_required = models.DecimalField(default=10.00, decimal_places=2, max_digits=12)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} group mentorship led by {self.mentor.username} in {self.category.name}"

# Deduct Points from Profile model when messaging or joining mentorship
class MentorshipTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mentorship_type = models.CharField(max_length=50, choices=[('one-on-one', 'One-on-One'), ('group', 'Group')])
    points_deducted = models.DecimalField(decimal_places=2, max_digits=12)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Points deducted for {self.mentorship_type} mentorship by {self.user.username}"

# Messaging between mentor and mentee (encrypted)
class MentorshipMessage(models.Model):
    sender = models.ForeignKey(User, related_name='sent_mentorship_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_mentorship_messages', on_delete=models.CASCADE)
    mentorship = models.ForeignKey(OneOnOneMentorship, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    group_mentorship = models.ForeignKey(GroupMentorship, on_delete=models.CASCADE, related_name="group_messages", null=True, blank=True)
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Encrypt the message before saving
        f = Fernet(settings.ENCRYPTION_KEY)
        self.message = f.encrypt(self.message.encode()).decode()
        super(MentorshipMessage, self).save(*args, **kwargs)

    def get_decrypted_message(self):
        # Decrypt the message when retrieving it
        f = Fernet(settings.ENCRYPTION_KEY)
        return f.decrypt(self.message.encode()).decode()

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"
