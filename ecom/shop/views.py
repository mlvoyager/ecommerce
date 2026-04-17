from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product, Rating, Order, OrderItem, AppEvaluation, Category
from django.core.paginator import Paginator
from django.db.models import Sum, Avg, Count
from django.http import JsonResponse
import json
from .chatbot import simple_bot

def chatbot(request):

    if request.method == "POST":

        data = json.loads(request.body)

        message = data["message"]

        reply = simple_bot(message)

        return JsonResponse({"reply": reply})

def index(request):
    product_objet = Product.objects.all()
    item_name = request.GET.get('item-name')
    if item_name!='' and item_name is not None:
        product_objet = Product.objects.filter(title__icontains=item_name)
    paginator = Paginator(product_objet,4)
    page = request.GET.get('page') #recuperer le numero de la page
    product_objet = paginator.get_page(page) #On affiche les produit d'une page
    return render(request, 'shop/index.html',{'product_objet':product_objet})



def detail(request, myid):
    product_objet = get_object_or_404(Product, id=myid)

    # Traitement du formulaire de notation
    if request.method == "POST":
        try:
            stars = int(request.POST.get('rating', 0) or 0)
        except ValueError:
            stars = 0
        if 1 <= stars <= 5:
            Rating.objects.create(product=product_objet, stars=stars)
        return redirect('detail', myid=myid)

    ratings = product_objet.ratings.all()
    average = product_objet.average_rating()
    context = {
        'product': product_objet,
        'ratings': ratings,
        'average': average,
    }
    return render(request,'shop/detail.html', context)


def cart_view(request):
    """
    Page panier : l'affichage des produits se fait côté JavaScript
    à partir de localStorage, mais on fournit la liste des produits
    pour pouvoir afficher les infos (prix, titre, image).
    """
    products = Product.objects.all()
    return render(request, 'shop/cart.html', {'products': products})


def checkout(request):
    """
    Page de commande : formulaire client + récapitulatif du panier.
    Le panier est envoyé en JSON via un champ caché.
    """
    if request.method == "POST":
        import json
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        cart_json = request.POST.get('cart') or "{}"

        try:
            cart = json.loads(cart_json)
        except Exception:
            cart = {}

        if not cart:
            return render(request, 'shop/checkout.html', {
                'error': "Votre panier est vide.",
            })

        # Création de la commande
        order = Order.objects.create(
            name=name or "Client",
            email=email or "",
            phone=phone or "",
            address=address or "",
            total=0,
        )

        total = 0
        for product_id, qty in cart.items():
            try:
                qty = int(qty)
            except (TypeError, ValueError):
                qty = 1
            if qty <= 0:
                continue
            try:
                product = Product.objects.get(id=int(product_id))
            except (Product.DoesNotExist, ValueError):
                continue
            line_total = product.price * qty
            total += line_total
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.price,
            )

        order.total = total
        order.save()

        # Après création de la commande, on redirige vers le module de paiement
        request.session['last_order_id'] = order.id
        return redirect('payment')

    return render(request, 'shop/checkout.html')


def app_evaluation(request):
    """
    Page d'évaluation globale de l'application.
    """
    if request.method == "POST":
        try:
            stars = int(request.POST.get('rating', 0) or 0)
        except ValueError:
            stars = 0
        comment = request.POST.get('comment', '')
        email = request.POST.get('email', '')
        if 1 <= stars <= 5:
            AppEvaluation.objects.create(stars=stars, comment=comment, email=email)
        return redirect('app_evaluation')

    evaluations = AppEvaluation.objects.all()
    avg = 0
    if evaluations.exists():
        from django.db.models import Avg
        avg = evaluations.aggregate(Avg('stars'))['stars__avg'] or 0

    context = {
        'evaluations': evaluations,
        'average_app': avg,
    }
    return render(request, 'shop/app_evaluation.html', context)


def categories_view(request):
    """
    Liste toutes les catégories et permet de filtrer les produits par catégorie.
    """
    categories = Category.objects.all()
    selected_id = request.GET.get('category')
    products = Product.objects.all()
    selected_category = None

    if selected_id:
        try:
            selected_category = Category.objects.get(id=int(selected_id))
            products = products.filter(Category=selected_category)
        except (Category.DoesNotExist, ValueError):
            selected_category = None

    paginator = Paginator(products, 8)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    context = {
        'categories': categories,
        'selected_category': selected_category,
        'products': products_page,
    }
    return render(request, 'shop/categories.html', context)




def admin_dashboard(request):
    """
    Tableau de bord admin simple (sans authentification avancée).
    Affiche les principaux indicateurs de l'application.
    """
    nb_products = Product.objects.count()
    nb_categories = Category.objects.count()
    nb_orders = Order.objects.count()
    revenue = Order.objects.aggregate(total=Sum('total'))['total'] or 0

    nb_ratings = Rating.objects.count()
    avg_product_rating = Rating.objects.aggregate(avg=Avg('stars'))['avg'] or 0

    nb_app_evals = AppEvaluation.objects.count()
    avg_app_rating = AppEvaluation.objects.aggregate(avg=Avg('stars'))['avg'] or 0

    last_orders = Order.objects.all()[:5]
    top_products = (
        Product.objects
        .annotate(total_sold=Sum('orderitem__quantity'))
        .order_by('-total_sold')[:5]
    )

    context = {
        'nb_products': nb_products,
        'nb_categories': nb_categories,
        'nb_orders': nb_orders,
        'revenue': revenue,
        'nb_ratings': nb_ratings,
        'avg_product_rating': avg_product_rating,
        'nb_app_evals': nb_app_evals,
        'avg_app_rating': avg_app_rating,
        'last_orders': last_orders,
        'top_products': top_products,
    }
    return render(request, 'shop/admin_dashboard.html', context)
