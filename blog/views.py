from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from .models import Post


# Create your views here.
def index(request):
    pass

def post_list(request):
    posts = Post.published.all()

    contex = {'posts': posts}
    return render(request, "blog/list.html", contex)

def post_detail(request, pk):
    # try:
    #     post = Post.published.get(id=pk)
    # except:
    #     raise Http404("No post found!")

    post = get_object_or_404(Post, id=pk, status=Post.Status.PUBLISHED)
    contex = {'post': post}

    return render(request, "blog/detail.html", contex)