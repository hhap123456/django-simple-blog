from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Post
from django.core import paginator
from django.views.generic import ListView, DetailView


# Create your views here.
def index(request):
    pass

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

# def post_detail(request, pk):
#     # try:
#     #     post = Post.published.get(id=pk)
#     # except:
#     #     raise Http404("No post found!")
#
#     post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
#     contex = {'post': post}
#     return render(request, "blog/detail.html", contex)

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
