from django.db import models

# Create your models here.
class StaffEmailConfiguration(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    name = models.CharField(max_length=100,default='Gmail Configuration')
    host = models.CharField(max_length=100,default='smtp.gmail.com')
    port = models.IntegerField(default=587)
    use_tls = models.BooleanField(default=True)
    username = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    staff_id = models.CharField(max_length=50, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.staff_id:
            # Generate staff ID
            first_letter = self.first_name[0].upper()
            last_letter = self.last_name[0].upper()
            print("First letter:", first_letter)
            print("Last letter:", last_letter)
            last_staff = StaffEmailConfiguration.objects.filter(first_name__startswith=first_letter, last_name__endswith=last_letter).order_by('-staff_id').first()
            if last_staff:
                print("Last staff ID:", last_staff.staff_id)
                last_sequence = int(last_staff.staff_id.split('KS')[0][-3:])  # Extract the sequence number correctly
                next_sequence = last_sequence + 1  # Increment the sequence by 1
                print("Next sequence:", next_sequence)
            else:
                next_sequence = 1  # Start from 1 if no previous staff records found
                print("No previous staff found.")
            sequence_str = str(next_sequence).zfill(3)  # Use next_sequence here
            print("Sequence string:", sequence_str)
            self.staff_id = f"{first_letter}{last_letter}{sequence_str}KS"
            print("Generated staff ID:", self.staff_id)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.staff_id}"