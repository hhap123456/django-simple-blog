from django.contrib.admin.templatetags.admin_list import results
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404

from .forms import TicketForm, CommentForm, PostForm, SearchForm
from .models import Post, Ticket
from django.core import paginator
from django.views.generic import ListView, DetailView
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity


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
    paginate_by = 3 # limit to 3 in a page
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

            return redirect('blog:post_list')
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


def post_form(request):
    user = request.user.is_authenticated
    user2 = request.user
    print(user)
    print(user2)

    if request.method == "POST":
        form = PostForm(data=request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:post_list')

    else:
        form = PostForm()

    context = {'form': form}
    return render(request, 'forms/post.html', context)

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
            results1 = Post.published.annotate(similarity=TrigramSimilarity('title', query),).\
                       filter(similarity__gt=0.1)
            results2 = Post.published.annotate(similarity=TrigramSimilarity('description', query),).\
                        filter(similarity__gt=0.1)
            results = (results1 | results2).order_by('-similarity')

    context = {
        'query': query,
        'results': results
    }

    return render(request, 'blog/search.html', context)

