from django.db import models
from django.contrib.auth.models import User

class MatrixItem(models.Model):
    filename = models.CharField(max_length = 100)
    fileID = models.CharField(max_length = 100)
    name = models.CharField(max_length = 400)
    email = models.EmailField()
    updates = models.CharField(max_length = 5)
    reported_Difficulty = models.CharField(max_length = 10)
    reported_CorrectAnswer = models.CharField(max_length = 5)
    timestampSubmitted = models.DateTimeField()
    filesize = models.IntegerField()
    filetype = models.CharField(max_length = 50)
    explanation = models.TextField()
    
    def checkedByUser(self, rater):
        try:
            IntegrityCheck.objects.get(matrixItem=self, rater = rater)
            return True
        except IntegrityCheck.DoesNotExist:
            return False

    def checkedAndAcceptedByUser(self, rater):
        try:
            check = IntegrityCheck.objects.get(matrixItem=self, rater = rater)
            return True, (check.correct and check.requirements)
        except IntegrityCheck.DoesNotExist:
            return False, False

    def acceptedByUser(self, rater):
        try:
            check = IntegrityCheck.objects.get(matrixItem=self, rater = rater)
            return check.correct and check.requirements
        except IntegrityCheck.DoesNotExist:
            return False

    def __unicode__(self):
        return self.fileID
    
class MatrixAnswer(models.Model):
    matrixItem = models.ForeignKey(MatrixItem)
    userName = models.CharField(max_length = 100)
    answer = models.IntegerField()
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    timeTaken = models.IntegerField()
    
class IntegrityCheck(models.Model):
    matrixItem = models.ForeignKey(MatrixItem)
    rater = models.ForeignKey(User)
    requirements = models.BooleanField()
    correct = models.BooleanField()
    nominated = models.BooleanField()
    comments = models.TextField()
    
    def __unicode__(self):
        return self.matrixItem.fileID
