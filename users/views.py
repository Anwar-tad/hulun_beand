from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from .forms import RegisterForm, ProductForm
from .models import Product,Category
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator


def register(request):
    if request.user.is_authenticated:
        return redirect('home') # ገብቶ ከሆነ ወደ መነሻ ገጽ መልሰው
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # ከተመዘገበ በኋላ በራስ-ሰር login እንዲያደርግ
            messages.success(request, f'Account created for {user.username}! Welcome!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})
def home(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    
    product_list = Product.objects.all().order_by('-created_at')

    if selected_category:
        product_list = product_list.filter(category__name=selected_category)

    paginator = Paginator(product_list, 6) # በአንድ ገጽ 6 እቃዎች
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category
    }
    return render(request, 'home.html', context)

@login_required # <-- ይህ decorator ተጠቃሚው ካልገባ ወደ login ገጽ ይልከዋል
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES) # request.FILES ለፎቶ ነው
        if form.is_valid():
            product = form.save(commit=False) # ዳታቤዝ ላይ ወዲያው አያስቀምጠው
            product.seller = request.user # ሻጩ አሁን የገባው ተጠቃሚ ነው
            product.save() # አሁን ዳታቤዝ ላይ ያስቀምጠዋል
            messages.success(request, 'Your product has been posted successfully!') # <-- መልዕክት ጨምር
            return redirect('home') # እቃውን ከለጠፈ በኋላ ወደ መነሻ ገጽ ይመልሰዋል
    else:
        form = ProductForm()
    
    return render(request, 'users/create_product.html', {'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    # ተመሳሳይ እቃዎችን ማግኘት
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)[:4] # እስከ 4 ተመሳሳይ እቃዎች
    
    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'users/product_detail.html', context)

@login_required
def product_update(request, pk):
    product = Product.objects.get(id=pk)
    if product.seller != request.user:
        # Optional: Add a message here that access is denied
        return redirect('home') # If the user is not the seller, redirect

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your product has been updated!') # <-- መልዕክት ጨምር
   
            return redirect('product_detail', pk=product.id)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form
    }
    return render(request, 'users/product_update.html', context)

@login_required
def product_delete(request, pk):
    product = Product.objects.get(id=pk)
    if product.seller != request.user:
        return redirect('home')

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Your product has been deleted.') # <-- መልዕክት ጨምር
        return redirect('home')
    
    context = {
        'product': product
    }
    return render(request, 'users/product_delete.html', context)

@login_required
def profile(request, username):
    user_products = Product.objects.filter(seller=request.user).order_by('-created_at')
    context = {
        'products': user_products
    }
    return render(request, 'users/profile.html', context)
# users/views.py
def home(request):
    query = request.GET.get('q') # የፍለጋ ቃሉን ከ URL ያገኛል
    if query:
        products = Product.objects.filter(name__icontains=query).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')
    
    context = {
        'products': products
    }
    return render(request, 'home.html', context)

