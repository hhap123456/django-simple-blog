from audioop import reverse

from django.contrib.admin.templatetags.admin_list import results, change_list_object_tools_tag
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template.context_processors import request
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation.template import context_re

from .forms import TicketForm, CommentForm, SearchForm, CreatePostForm, \
    UserRegistrationForm, UserEditForm, AccountEditForm  # , LoginForm  # , PostForm
from .models import Post, Ticket, Image, Account, User
from django.core import paginator
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
def index(request):
    return render(request, 'blog/index.html')

def post_list(request, category=None):
    if category:
        posts = Post.objects.filter(category=category)
    else:
        posts = Post.published.all()
    paginator = Paginator(posts, 3)  # Pagination
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)

    contex = {
        'posts': posts,
        'category': category,
        'users': User.objects.all(),
    }

    return render(request, "blog/list.html", contex)

# class PostListView(ListView):
#     #model = Post    # -> Post.object.all()
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 5 # limit to 3 in a page
#     template_name = 'blog/list.html'

def post_detail(request, pk):
    # try:
    #     post = Post.published.get(id=pk)
    # except:
    #     raise Http404("No post found!")

    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    contex = {
        'post': post,
        'form': form,
        'comments': comments,
      }
    return render(request, "blog/detail.html", contex)

# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'blog/detail.html'

def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            ticket_obj = Ticket.objects.create(massage=cd['massage'],
                                               name=cd['name'],
                                               email=cd['email'],
                                               phone=cd['phone'],
                                               subject=cd['subject'],
                                               )
            # ticket_obj = Ticket.objects.create()
            # ticket_obj.massage = cd['massage']
            # ticket_obj.name = cd['name']
            # ticket_obj.email = cd['email']
            # ticket_obj.phone = cd['phone']
            # ticket_obj.subject = cd['subject']
            # ticket_obj.save()

            if request.user.is_authenticated():
                return redirect('blog:profile')
            else:
                return redirect('blog:index')
    else:
        form = TicketForm()

    return render(request,  'forms/ticket.html', {'form': form})


def post_comment(request, pk):
    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    context = {'post': post, 'form': form, 'comment': comment}
    return render(request, 'forms/comment.html', context )


# def post_form(request):
#     if request.method == "POST":
#         form = PostForm(data=request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user
#             post.save()
#             return redirect('blog:post_list')
#
#     else:
#         form = PostForm()
#
#     context = {'form': form}
#     return render(request, 'forms/post.html', context)

def post_search(request):
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
        # -0-
            # results1 = Post.published.filter(description__icontains=query)
            # results2 = Post.published.filter(title__icontains=query)
            # results = results1 | results2

        # Q object
            # results = Post.published.filter(Q(title__icontains=query) | Q(description__icontains=query))

            # postgres FTS
        # -1-
                # results = Post.published.filter(Q(title__search=query) | Q(description__search=query))
        # -2-
                # results = Post.published.annotate(search = SearchVector('title',
                #                                                    'description')).filter(search=query)
        # -3-
                # search_query = SearchQuery(query)
                # search_query = SearchQuery(query) | SearchQuery('word')
                #results = Post.published.annotate(search=SearchVector('title',
                #                                                    'description')).filter(search=search_query)
        # -4-
            # search_query = SearchQuery(query)
            # search_vector = (SearchVector('title', weight="A") +
            #                  SearchVector('description', weight="B"))
            #
            # results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query))\
            #     .filter(rank__gte=0.3).order_by('-rank')
                    # filter(search=search_query)
        # -5- TrigramSimilarity
            post_results1 = Post.published.annotate(similarity=TrigramSimilarity('title', query),).\
                filter(similarity__gt=0.1)
            post_results2 = Post.published.annotate(similarity=TrigramSimilarity('description', query),).\
                filter(similarity__gt=0.1)


            # Search in the Image model
            image_results1 = Image.objects.annotate(similarity=TrigramSimilarity('title', query),) \
                    .filter(similarity__gt=0.1)

            image_results2 = Image.objects.annotate(similarity=TrigramSimilarity('description', query),)\
                    .filter(similarity__gt=0.1)

            post_results = (post_results1 | post_results2 ).order_by('-similarity')
            image_results = (image_results1 | image_results2 ).order_by('-similarity')

            combined_results = list(post_results) + list(image_results)

            results = sorted(combined_results, key=lambda x: x.similarity, reverse=True)

    context = {
        'query': query,
        'results': results
    }

    return render(request, 'blog/search.html', context)

# @login_required
# def profile(request):
#     user = request.user
#     posts = Post.published.filter(author=user)
#
#     return render(request, 'blog/profile.html', {'posts': posts})



class Profile(LoginRequiredMixin, ListView):
    template_name = 'blog/profile.html'
    context_object_name = 'posts'
    paginate_by = 5
    login_url = reverse_lazy('blog:login')

    def get_queryset(self):
        return Post.published.filter(author=self.request.user)

@login_required
def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)  # request.FILES -> for files ( images )

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            image1 = form.cleaned_data['image1']
            image2 = form.cleaned_data['image2']

            if image1:
                Image.objects.create(image_file= image1, post=post,)
            if image2:
                Image.objects.create(image_file= image2, post=post,)

            return redirect('blog:post_list')

    else:
        form = CreatePostForm()

    return render(request, 'forms/create-post.html', {'form': form})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect('blog:profile')

    else:
        return render(request, 'forms/delete-post.html', {'post': post})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES, instance=post)  # instance -> when obj is available

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            Image.objects.create(image_file= form.cleaned_data['image1'], post=post,)
            Image.objects.create(image_file= form.cleaned_data['image2'], post=post,)

            return redirect('blog:post_list')

    else:
        form = CreatePostForm(instance=post)

    return render(request, 'forms/create-post.html', {'form': form, 'post': post})


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)

    image.delete()
    return redirect('blog:profile')


# def user_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request, username=cd['username'], password=cd['password'])
#
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('blog:profile')
#                 else:
#                     return HttpResponse('Your account is disabled.')
#
#             else:
#                 return HttpResponse('Invalid login credentials.')
#
#     else:
#         form = LoginForm()
#         return render(request,'forms/login.html', {'form': form})

def user_logout(request):
    logout(request)
    # return redirect('blog:index')
    return redirect(request.META.get('HTTP_REFERER')) # go to previous page

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password2'])    # set_password -> save as hash
            user.save()
            Account.objects.create(user=user)
            return render(request, 'registration/register_done.html', {'user': user})

    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form' : form})

@login_required
def edit_account(request):
    if request.method == "POST":
        user_form = UserEditForm(request.POST, instance=request.user)
        account_form = AccountEditForm(request.POST, request.FILES, instance=request.user.account)
        if account_form.is_valid() and user_form.is_valid():
            account_form.save()
            user_form.save()

    else:
        user_form = UserEditForm(instance=request.user)
        account_form = AccountEditForm(instance=request.user.account)

    context = {
        'user_form': user_form,
        'account_form': account_form
               }
    return render(request, 'registration/edit_account.html', context)


def author_detail(request, pk):
    user = get_object_or_404(User, id=pk)
    account = user.account

    context = {
        'user': user,
        'account': account,
    }
    return render(request, 'blog/author-detail.html', context)


@login_required()
def author_comment_dashboard(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        'comments' : post.comments.filter(active=True).all(),
        'post': post
    }
    if request.user == post.author:
        return render(request, 'blog/author_comment_dashboard.html', context)
    else:
        return Http404



# ------registration views START
class CustomLoginViews(auth_views.LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        """Custom redirect after login"""
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('blog:index')

    def get_redirect_url(self):
        """Override to handle the next parameter safely"""
        redirect_to = self.request.POST.get(
            self.redirect_field_name,
            self.request.GET.get(self.redirect_field_name)
        )
        if redirect_to:
            return redirect_to
        return self.success_url


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('blog:index')


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Password Reset Sent'  # Add any custom context
        return context

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'  # Custom template
    success_url = reverse_lazy('blog:login')  # Redirect after successful password reset

    def form_valid(self, form):
        # Add custom logic before saving the new password
        response = super().form_valid(form)
        # Example: Logging or sending a custom notification
        return response

class CustomPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'registration/password_change.html'
    success_url = reverse_lazy('blog:password_change_done')

    def form_valid(self, form):
        # Add custom logic before saving
        response = super().form_valid(form)
        # Add custom logic after saving
        return response

class CustomPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'registration/password_change_done.html'

# ------registration views END