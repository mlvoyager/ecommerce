from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now=True)


    class Meta:
        ordering =['-date_added'] #classer par order d'ajout


    def __str__(self):
        return self.name




class Product(models.Model):
    title = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    Category = models.ForeignKey(Category, related_name='category',on_delete=models.CASCADE)
    image = models.CharField(max_length=5000)
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering =['-date_added'] #classer par order d'ajout
    
    def __str__(self):
        return self.title

    def average_rating(self):
        """
        Retourne la moyenne des étoiles pour ce produit (0 si aucune note).
        """
        from django.db.models import Avg
        agg = self.ratings.aggregate(Avg('stars'))
        return agg.get('stars__avg') or 0


class Rating(models.Model):
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.title} - {self.stars} étoile(s)"


class Order(models.Model):
    """
    Commande passée par un client à partir du panier.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.FloatField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Commande #{self.id} - {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(help_text="Prix unitaire au moment de la commande")

    def __str__(self):
        return f"{self.product.title} x {self.quantity}"


class AppEvaluation(models.Model):
    """
    Évaluation globale de l'application (note + commentaire).
    """
    stars = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Avis ({self.stars}/5)"
