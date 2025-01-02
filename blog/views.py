from django.contrib.admin.templatetags.admin_list import results
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404

from .forms import TicketForm, CommentForm, SearchForm, CreatePostForm, LoginForm  # , PostForm
from .models import Post, Ticket, Image
from django.core import paginator
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    return render(request, 'blog/index.html')

# def post_list(request):
#     posts = Post.published.all()
#     paginator = Paginator(posts, 3)  # Pagination
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#
#     contex = {
#         'posts': posts
#     }
#
#     return render(request, "blog/list.html", contex)

class PostListView(ListView):
    #model = Post    # -> Post.object.all()
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 5 # limit to 3 in a page
    template_name = 'blog/list.html'

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

            return redirect('blog:profile')
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


def profile(request):
    user = request.user
    posts = Post.published.filter(author=user)

    return render(request, 'blog/profile.html', {'posts': posts})


def create_post(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES)  # request.FILES -> for files ( images )

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            Image.objects.create(image_file= form.cleaned_data['image1'], post=post,)
            Image.objects.create(image_file= form.cleaned_data['image2'], post=post,)

            return redirect('blog:post_list')

    else:
        form = CreatePostForm()

    return render(request, 'forms/create-post.html', {'form': form})


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        post.delete()
        return redirect('blog:profile')

    else:
        return render(request, 'forms/delete-post.html', {'post': post})


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


def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)

    image.delete()
    return redirect('blog:profile')


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('blog:profile')
                else:
                    return HttpResponse('Your account is disabled.')

            else:
                return HttpResponse('Invalid login credentials.')

    else:
        form = LoginForm()
        return render(request,'forms/login.html', {'form': form})