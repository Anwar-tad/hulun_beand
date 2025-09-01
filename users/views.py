# users/views.py

# ==================================
# ==== 1. Import Statements ====
# ==================================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import FAQ  # FAQ ሞዴሉን አስገባ

# Import Forms
from .forms import (
    RegisterForm, 
    ProductForm, 
    UserUpdateForm, 
    ProfileUpdateForm
)

# Import Models
from .models import (
    Product, 
    Category, 
    ProductImage, 
    Profile, 
    Conversation, 
    Message
)

# ===============================================
# ==== 2. User Authentication & Profile Views ====
# ===============================================

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}! Welcome!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def profile(request, username):
    profile_owner = get_object_or_404(User, username=username)
    user_products = Product.objects.filter(seller=profile_owner).order_by('-created_at')
    context = {
        'profile_user': profile_owner,
        'products': user_products
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/profile_update.html', context)

# ===================================
# ==== 3. Product & Core Views ====
# ===================================

def home(request):
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    query = request.GET.get('q')

    product_list = Product.objects.all().order_by('-created_at')

    if selected_category:
        product_list = product_list.filter(category__name=selected_category)
    
    if query:
        product_list = product_list.filter(name__icontains=query)

    paginator = Paginator(product_list, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category
    }
    return render(request, 'home.html', context)

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            messages.success(request, 'Your product has been posted successfully!')
            return redirect('home')
    else:
        form = ProductForm()
    
    return render(request, 'users/create_product.html', {'form': form})

def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    related_products = Product.objects.filter(category=product.category).exclude(id=pk)[:4]
    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'users/product_detail.html', context)

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    if product.seller != request.user:
        messages.error(request, "You are not authorized to edit this product.")
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            new_images = request.FILES.getlist('images')
            if new_images:
                product.images.all().delete()
                for image in new_images:
                    ProductImage.objects.create(product=product, image=image)
            messages.success(request, 'Your product has been updated!')
            return redirect('product_detail', pk=product.id)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product
    }
    return render(request, 'users/product_update.html', context)

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, id=pk) # Using get_object_or_404 is safer
    if product.seller != request.user:
        return redirect('home')

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Your product has been deleted.')
        return redirect('home')
    
    context = { 'product': product }
    return render(request, 'users/product_delete.html', context)

# ========================================
# ==== 4. Like/Dislike & Social Views ====
# ========================================

@login_required
def like_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    if product.dislikes.filter(id=request.user.id).exists():
        product.dislikes.remove(request.user)
    if product.likes.filter(id=request.user.id).exists():
        product.likes.remove(request.user)
    else:
        product.likes.add(request.user)
    return redirect('product_detail', pk=product.id)

@login_required
def dislike_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    if product.likes.filter(id=request.user.id).exists():
        product.likes.remove(request.user)
    if product.dislikes.filter(id=request.user.id).exists():
        product.dislikes.remove(request.user)
    else:
        product.dislikes.add(request.user)
    return redirect('product_detail', pk=product.id)

# ================================
# ==== 5. Chat & Message Views ====
# ================================

@login_required
def start_conversation(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    if product.seller == request.user:
        messages.error(request, "You cannot start a conversation on your own product.")
        return redirect('product_detail', pk=product_pk)
    
    conversation = Conversation.objects.filter(product=product, participants=request.user).filter(participants=product.seller).first()

    if not conversation:
        conversation = Conversation.objects.create(product=product)
        conversation.participants.add(request.user, product.seller)

    return redirect('conversation_detail', pk=conversation.pk)

@login_required
def inbox(request):
    conversations = request.user.conversations.all()
    context = { 'conversations': conversations }
    return render(request, 'users/inbox.html', context)

@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    if request.user not in conversation.participants.all():
        messages.error(request, "You are not authorized to view this conversation.")
        return redirect('inbox')
    
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(conversation=conversation, sender=request.user, content=content)
            return redirect('conversation_detail', pk=pk)

    context = { 'conversation': conversation }
    return render(request, 'users/conversation_detail.html', context)

def help_page(request):
    faqs = FAQ.objects.all().order_by('order')
    context = {'faqs': faqs}
    return render(request, 'help.html', context)
