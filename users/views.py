from django.db.models import Q # ይህንን ጨምር
from .models import Conversation, Message 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required 
from .forms import RegisterForm, ProductForm
from .models import Product,Category, ProductImage
from django.contrib.auth import login
from django.contrib import messages
from django.core.paginator import Paginator
from .forms import UserUpdateForm, ProfileUpdateForm # አዲሶቹን ፎርሞች እናስገባለን
from django.contrib.auth.models import User
from django.http import JsonResponse

@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
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
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(product=product, image=image)
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
# users/views.py

@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    # ሻጩ ትክክለኛ መሆኑን ማረጋገጥ
    if product.seller != request.user:
        messages.error(request, "You are not authorized to edit this product.")
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save() # የጽሑፍ መረጃውን ያስቀምጣል

            # --- አዲስ የምንጨምረው የፎቶ ማስተናገጃ ክፍል ---
            new_images = request.FILES.getlist('images')
            if new_images:
                # ተጠቃሚው አዲስ ፎቶ ከሰቀለ፣ የድሮዎቹን በሙሉ እናጠፋለን
                # (ይህ አንድ አማራጭ ነው፤ የድሮዎቹም እንዲቆዩ ማድረግ ይቻላል)
                product.images.all().delete()
                for image in new_images:
                    ProductImage.objects.create(product=product, image=image)
            # --- አዲስ የምንጨምረው ክፍል እዚህ ያበቃል ---

            messages.success(request, 'Your product has been updated!')
            return redirect('product_detail', pk=product.id)
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product # የድሮ ፎቶዎችን ለማሳየት
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

def profile(request, username):
    # 1. Get the user object for the profile being viewed
    profile_owner = get_object_or_404(User, username=username)

    # 2. Filter products that belong ONLY to that user
    user_products = Product.objects.filter(seller=profile_owner).order_by('-created_at')

    # 3. Create the context dictionary to send to the template
    context = {
        'profile_user': profile_owner, # The user whose profile it is
        'products': user_products      # The list of their products
    }
    
    # 4. Render the template with the context
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
    
@login_required
def like_product(request, pk):
    product = get_object_or_404(Product, id=pk)
    
    # ተጠቃሚው ከዚህ በፊት dislike አድርጎ ከሆነ ከ dislike ዝርዝር ውስጥ እናስወግደዋለን
    if product.dislikes.filter(id=request.user.id).exists():
        product.dislikes.remove(request.user)

    # ተጠቃሚው ከዚህ በፊት like አድርጎ ከሆነ ከ like ዝርዝር ውስጥ እናስወግደዋለን (unlike)
    if product.likes.filter(id=request.user.id).exists():
        product.likes.remove(request.user)
    # ካልሆነ ደግሞ እንጨምረዋለን (like)
    else:
        product.likes.add(request.user)
    
    # ገጹን refresh ሳናደርግ የ like/dislike ቁጥሩን ለማዘመን
    return redirect('product_detail', pk=product.id)


@login_required
def dislike_product(request, pk):
    product = get_object_or_404(Product, id=pk)

    # ተጠቃሚው ከዚህ በፊት like አድርጎ ከሆነ ከ like ዝርዝር ውስጥ እናስወግደዋለን
    if product.likes.filter(id=request.user.id).exists():
        product.likes.remove(request.user)

    # ተጠቃሚው ከዚህ በፊት dislike አድርጎ ከሆነ ከ dislike ዝርዝር ውስጥ እናስወግደዋለን (undislike)
    if product.dislikes.filter(id=request.user.id).exists():
        product.dislikes.remove(request.user)
    # ካልሆነ ደግሞ እንጨምረዋለን (dislike)
    else:
        product.dislikes.add(request.user)
        
    return redirect('product_detail', pk=product.id)

# --- አዲስ የምንጨምራቸው የ Chat ቪዎች ---
@login_required
def start_conversation(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    
    # ገዢው ለራሱ እቃ መልዕክት እንዳይልክ መከልከል
    if product.seller == request.user:
        messages.error(request, "You cannot start a conversation on your own product.")
        return redirect('product_detail', pk=product_pk)

    # ገዢው እና ሻጩ ከዚህ በፊት በዚህ እቃ ላይ ውይይት ጀምረው እንደሆነ ማረጋገጥ
    conversation = Conversation.objects.filter(product=product, participants=request.user).filter(participants=product.seller).first()

    # ውይይት ከሌለ፣ አዲስ እንፈጥራለን
    if not conversation:
        conversation = Conversation.objects.create(product=product)
        conversation.participants.add(request.user, product.seller)

    return redirect('conversation_detail', pk=conversation.pk)

@login_required
def inbox(request):
    # ተጠቃሚው ተሳታፊ የሆነባቸውን ውይይቶች በሙሉ ማምጣት
    conversations = request.user.conversations.all()
    context = {
        'conversations': conversations
    }
    return render(request, 'users/inbox.html', context)

@login_required
def conversation_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    
    # ተጠቃሚው የዚህ ውይይት ተሳታፊ መሆኑን ማረጋገጥ
    if request.user not in conversation.participants.all():
        messages.error(request, "You are not authorized to view this conversation.")
        return redirect('inbox')
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    # አዲስ መልዕክት ከተላከ
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(conversation=conversation, sender=request.user, content=content)
            return redirect('conversation_detail', pk=pk)

    context = {
        'conversation': conversation
    }
    return render(request, 'users/conversation_detail.html', context)

