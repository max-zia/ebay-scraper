from django.db import models

class Search(models.Model):
    searchterm = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.searchterm[:10]