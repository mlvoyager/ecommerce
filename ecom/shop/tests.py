from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Rating, AppEvaluation


class CategoryModelTests(TestCase):
    def test_str_returns_name(self):
        category = Category.objects.create(name="Informatique")
        self.assertEqual(str(category), "Informatique")


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Informatique")
        self.product = Product.objects.create(
            title="Ordinateur portable",
            price=999.99,
            description="Un bon ordinateur",
            Category=self.category,
            image="image.jpg",
        )

    def test_str_returns_title(self):
        self.assertEqual(str(self.product), "Ordinateur portable")

    def test_average_rating_without_ratings_is_zero(self):
        self.assertEqual(self.product.average_rating(), 0)

    def test_average_rating_with_ratings(self):
        Rating.objects.create(product=self.product, stars=4)
        Rating.objects.create(product=self.product, stars=2)
        self.assertEqual(self.product.average_rating(), 3)


class IndexViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Informatique")
        Product.objects.create(
            title="Clavier",
            price=29.99,
            description="Clavier mécanique",
            Category=self.category,
            image="clavier.jpg",
        )

    def test_index_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_index_lists_product(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Clavier")

    def test_index_search_filters_products(self):
        Product.objects.create(
            title="Souris",
            price=9.99,
            description="Souris optique",
            Category=self.category,
            image="souris.jpg",
        )
        response = self.client.get(reverse('home'), {'item-name': 'Clavier'})
        self.assertContains(response, "Clavier")
        self.assertNotContains(response, "Souris")


class DetailViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Informatique")
        self.product = Product.objects.create(
            title="Ecran",
            price=149.99,
            description="Ecran 24 pouces",
            Category=self.category,
            image="ecran.jpg",
        )

    def test_detail_status_code(self):
        response = self.client.get(reverse('detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)

    def test_detail_unknown_product_returns_404(self):
        response = self.client.get(reverse('detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_posting_valid_rating_creates_rating(self):
        response = self.client.post(
            reverse('detail', args=[self.product.id]), {'rating': 5}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.product.ratings.count(), 1)
        self.assertEqual(self.product.ratings.first().stars, 5)

    def test_posting_invalid_rating_is_ignored(self):
        self.client.post(reverse('detail', args=[self.product.id]), {'rating': 42})
        self.assertEqual(self.product.ratings.count(), 0)


class CategoriesViewTests(TestCase):
    def test_categories_status_code(self):
        response = self.client.get(reverse('categories'))
        self.assertEqual(response.status_code, 200)


class AppEvaluationViewTests(TestCase):
    def test_get_status_code(self):
        response = self.client.get(reverse('app_evaluation'))
        self.assertEqual(response.status_code, 200)

    def test_posting_valid_evaluation_creates_entry(self):
        response = self.client.post(reverse('app_evaluation'), {
            'rating': 4,
            'comment': 'Top',
            'email': 'test@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AppEvaluation.objects.count(), 1)


class AdminDashboardViewTests(TestCase):
    def test_dashboard_status_code(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
