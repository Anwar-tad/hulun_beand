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
from django.urls import get_resolver
from .models import UserTier
from .forms import RetailProductForm
from .forms import WholesaleProductForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import json

# Import Forms
from .forms import (
    RegisterForm, 
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

def handle_product_creation(request, form_class, is_wholesale=False):
    """Handles product creation for both retail and wholesale products."""
    form = form_class(request.POST, request.FILES)
    if form.is_valid():
        product = form.save(commit=False)
        product.seller = request.user
        if is_wholesale:
            product.is_wholesale = True
        product.save()
        
        # Handle Image Uploads (Common Logic)
        images = request.FILES.getlist('images')
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        
        return product  # Return the created product
    return None

@login_required
def premium_upgrade(request):
    """Premium membership upgrade page - COMBINED VERSION"""
    user_tier, created = UserTier.objects.get_or_create(user=request.user)
    profile, profile_created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        plan_type = request.POST.get('plan_type')
        tier_type = request.POST.get('tier_type', 'wholesale')
        
        # Update user tier
        user_tier.tier = tier_type
        user_tier.is_paid = True
        
        # Set expiration date based on plan
        if plan_type == 'monthly':
            user_tier.paid_until = timezone.now() + timedelta(days=30)
            profile.premium_until = timezone.now() + timedelta(days=30)
        elif plan_type == 'annual':
            user_tier.paid_until = timezone.now() + timedelta(days=365)
            profile.premium_until = timezone.now() + timedelta(days=365)
        
        user_tier.save()
        
        # Update profile
        profile.is_premium_member = True
        profile.is_wholesaler = (tier_type == 'wholesale')
        profile.premium_since = timezone.now()
        profile.premium_type = plan_type
        
        profile.save()
        
        messages.success(request, "Premium upgrade successful!")

        # Check if business verification is needed for wholesale
        if tier_type == 'wholesale' and not profile.business_verified:
            return redirect('business_verification')
        
        return redirect('premium_success')
    
    context = {
        'user_tier': user_tier,
        'user_profile': profile,
    }
    return render(request, 'users/premium_upgrade.html', context)

# ይህንን የተደጋገመ ተግባር ሰርዝ (ከላይ ባለው ኮድ ውስጥ አንድ ጊዜ ብቻ)
# የሚከተለውን ያጥፉ:
# @login_required
# def premium_upgrade(request):  # ይህ ሁለተኛው ተግባር ነው - ይሰረዝ
def has_wholesale_access(user):
    """Check if user has wholesale access"""
    try:
        user_tier = UserTier.objects.get(user=user)
        return user_tier.tier == 'wholesale' and user_tier.is_paid
    except UserTier.DoesNotExist:
        return False


@login_required
def wholesale_dashboard(request):
    """Wholesale dashboard for premium users"""
    if not has_wholesale_access(request.user):
        messages.error(request, "You need premium access to view this page")
        return redirect('premium_upgrade')
    
    return render(request, 'wholesale/dashboard.html')

@login_required
def premium_success(request):
    """Premium upgrade success page"""
    if not has_wholesale_access(request.user):
        return redirect('premium_upgrade')
    
    return render(request, 'users/premium_success.html')

@login_required
def wholesale_products(request):
    """Wholesale products management"""
    if not has_access_to_wholesale(request.user):
        return redirect('premium_upgrade')
    
    products = Product.objects.filter(seller=request.user, is_wholesale=True)
    return render(request, 'wholesale/products.html', {'products': products})

@login_required
def wholesale_suppliers(request):
    """Wholesale suppliers directory"""
    if not has_access_to_wholesale(request.user):
        return redirect('premium_upgrade')
    
    # Get verified wholesale suppliers
    suppliers = Profile.objects.filter(
        is_wholesaler=True, 
        business_verified=True
    )
    return render(request, 'wholesale/suppliers.html', {'suppliers': suppliers})

@login_required
def wholesale_orders(request):
    """Wholesale orders management"""
    if not has_access_to_wholesale(request.user):
        return redirect('premium_upgrade')
    
    return render(request, 'wholesale/orders.html')

# Helper function to check wholesale access
def has_access_to_wholesale(user):
    """Check if user has access to wholesale features"""
    try:
        user_tier = UserTier.objects.get(user=user)
        profile = Profile.objects.get(user=user)
        return (user_tier.tier == 'wholesale' and 
                user_tier.is_paid and 
                profile.is_premium_active() and 
                profile.business_verified)
    except (UserTier.DoesNotExist, Profile.DoesNotExist):
        return False

@login_required
def premium_wholesale(request):
    """Premium wholesale platform access"""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = Profile.objects.create(user=request.user)
    
    # Check if user has wholesale tier
    user_tier, created = UserTier.objects.get_or_create(user=request.user)
    if user_tier.tier != 'wholesale' or not user_tier.is_paid:
        return redirect('premium_upgrade')
    
    # Check premium status
    if not profile.is_premium_active():
        return redirect('premium_upgrade')
    
    # Check business verification for wholesale access
    if not profile.business_verified:
        return redirect('business_verification')
    
    # Render premium platform
    context = {
        'user_profile': profile,
        'premium_type': profile.premium_type,
        'premium_until': profile.premium_until,
        'user_tier': user_tier,
    }
    return render(request, 'users/premium_wholesale.html', context)
@login_required
def business_verification(request):
    """Business verification form"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle form submission
        profile.business_name = request.POST.get('business_name', '')
        profile.business_type = request.POST.get('business_type', '')
        
        # Handle file uploads
        if 'business_license' in request.FILES:
            profile.business_license = request.FILES['business_license']
        if 'tax_clearance' in request.FILES:
            profile.tax_clearance = request.FILES['tax_clearance']
        if 'id_document' in request.FILES:
            # You might want to add this field to your Profile model
            # For now, we'll handle it if it exists
            if hasattr(profile, 'id_document'):
                profile.id_document = request.FILES['id_document']
        
        # Auto-approve for demo (in production, this would require admin review)
        profile.business_verified = True
        profile.verification_status = 'approved'  # Add this field to your model
        
        profile.save()
        
        messages.success(request, "Business verification submitted successfully!")
        return redirect('verification_success')
    
    context = {
        'profile': profile,
        'verification_steps': [
            {'number': 1, 'title': 'Submit Documents', 'active': True, 'completed': False},
            {'number': 2, 'title': 'Under Review', 'active': False, 'completed': False},
            {'number': 3, 'title': 'Verification Complete', 'active': False, 'completed': False},
        ]
    }
    return render(request, 'users/business_verification.html', context)

@login_required
def check_premium_status(request):
    """API endpoint to check premium status"""
    profile = getattr(request.user, 'profile', None)
    user_tier = getattr(request.user, 'usertier', None)
    
    if not profile:
        profile = Profile.objects.create(user=request.user)
    if not user_tier:
        user_tier = UserTier.objects.create(user=request.user)
    
    return JsonResponse({
        'is_premium': profile.is_premium_active(),
        'premium_type': profile.premium_type,
        'premium_until': profile.premium_until.isoformat() if profile.premium_until else None,
        'business_verified': profile.business_verified,
        'user_tier': user_tier.tier,
        'tier_paid': user_tier.is_paid,
        'tier_valid_until': user_tier.paid_until.isoformat() if user_tier.paid_until else None,
    })

# Success pages
@login_required
def premium_success(request):
    return render(request, 'users/premium_success.html')

@login_required
def verification_success(request):
    """Verification success page"""
    profile = get_object_or_404(Profile, user=request.user)
    
    context = {
        'business_name': profile.business_name,
        'verification_date': timezone.now(),
    }
    return render(request, 'users/verification_success.html', context)

@login_required
def switch_to_wholesale(request):
    """Switch user tier to wholesale"""
    user_tier, created = UserTier.objects.get_or_create(user=request.user)
    
    if user_tier.tier != 'wholesale':
        user_tier.tier = 'wholesale'
        user_tier.save()
        messages.info(request, _("Switched to wholesale mode. Upgrade to premium for full access."))
    
    return redirect('premium_upgrade')
# Add this to your views.py temporarily to debug


def debug_urls(request):
    resolver = get_resolver()
    url_patterns = []
    for pattern in resolver.url_patterns:
        if hasattr(pattern, 'url_patterns'):
            # This is an include
            for sub_pattern in pattern.url_patterns:
                if hasattr(sub_pattern, 'name') and sub_pattern.name:
                    url_patterns.append(sub_pattern.name)
        elif hasattr(pattern, 'name') and pattern.name:
            url_patterns.append(pattern.name)
    
    return HttpResponse(f"Available URL names: {sorted(url_patterns)}")
@login_required
def switch_to_standard(request):
    """Switch user tier to standard"""
    user_tier, created = UserTier.objects.get_or_create(user=request.user)
    
    if user_tier.tier != 'standard':
        user_tier.tier = 'standard'
        user_tier.is_paid = False
        user_tier.paid_until = None
        user_tier.save()
        messages.info(request, _("Switched to standard mode."))
    
    return redirect('home')

def upgrade_account(request):
    if request.method == 'POST':
        # Process payment and upgrade user
        request.user.profile.is_premium_member = True
        request.user.profile.premium_expiry = timezone.now() + timedelta(days=30)
        request.user.profile.premium_level = request.POST.get('plan', 'professional')
        request.user.profile.save()
        
        messages.success(request, 'Your account has been upgraded to premium!')
        return redirect('premium_wholesale')
    
    return render(request, 'users/upgrade.html')
@login_required
def premium_wholesale(request):
    if not request.user.profile.is_premium_member:
        return redirect('upgrade_page')
    return render(request, 'users/premium_wholesale.html')
    
def payment_required_view(request):
    return render(request, 'payment_required.html')
    # users/views.py

@login_required
def create_retail_product(request):
    if request.method == 'POST':
        product = handle_product_creation(request, RetailProductForm)
        if product:
            messages.success(request, 'Your product has been posted successfully!')
            return redirect('home')
    else:
        form = RetailProductForm()
    return render(request, 'users/create_product.html', {'form': form})

@login_required
def create_wholesale_product(request):
    if request.method == 'POST':
        product = handle_product_creation(request, WholesaleProductForm, is_wholesale=True)
        if product:
            messages.success(request, 'Your wholesale product has been posted successfully!')
            return redirect('some-success-page')  # You should change this URL
    else:
        form = WholesaleProductForm()
    return render(request, 'users/create_product.html', {'form': form})
def wholesale_view(request):
    try:
        user_tier = UserTier.objects.get(user=request.user)
        if user_tier.tier == 'wholesale' and user_tier.is_paid:
            wholesale_products = Product.objects.filter(is_wholesale=True).order_by('-created_at')
            context = {'wholesale_products': wholesale_products}
            return render(request, 'wholesale.html', context)
        else:
            return redirect('payment_required')
    except UserTier.DoesNotExist:
        return redirect('payment_required')

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
    product_list = Product.objects.filter(is_wholesale=False).order_by('-created_at')
    #product_list = Product.objects.all().order_by('-created_at') -->

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
        form = RetailProductForm(request.POST, request.FILES)
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
        form = RetailProductForm()    
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

    if product.is_wholesale:
        FormClass = WholesaleProductForm
    else:
        FormClass = BaseProductForm

    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # Handle image deletions
            existing_image_ids = request.POST.getlist('existing_images')
            for image in product.images.all():
                if str(image.id) not in existing_image_ids:
                    image.delete()

            # Handle image uploads
            new_images = request.FILES.getlist('images')
            for image in new_images:
                ProductImage.objects.create(product=product, image=image)

            messages.success(request, 'Your product has been updated!')
            return redirect('product_detail', pk=product.id)
    else:
        form = FormClass(instance=product)

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

# ... ከሌሎች view ተግባራት በኋላ ...

def wholesale_home(request):
    # ለአሁን ባዶ view እንጨምራለን
    return render(request, 'wholesale/home.html')

def job_listings(request):
    return render(request, 'jobs/listings.html')

def tenders(request):
    return render(request, 'tenders/list.html')

def real_estate(request):
    return render(request, 'real_estate/list.html')

def vehicles(request):
    return render(request, 'vehicles/list.html')

def services(request):
    return render(request, 'services/list.html')

def healthcare(request):
    return render(request, 'healthcare/list.html')
