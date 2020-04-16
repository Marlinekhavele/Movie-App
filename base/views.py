from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from .forms import *
from django.db.models import Avg

# Create your views here.

def home(request):
    movies = {}
    if 'title' in request.GET:
        title = request.GET['title']
        url = 'https://api.themoviedb.org/3/movie/550?api_key=c76fb0e97e8122287cfe28d173567350' % title
        response = requests.get(url)
        movies = response.json()
    return render(request, 'base/index.html', {'movies': movies})


# def home(request):
#     query = request.GET.get("title")
#     allMovies = None
#     if query:
#         allMovies = Movie.objects.filter(name__icontains=query)
#     else:
#         allMovies = Movie.objects.all()  # select * from movie

#     context = {
#         "movies": allMovies,
#     }

#     return render(request, "base/index.html", context)


# detail page
def detail(request, id):
    movie = Movie.objects.get(id=id)  # select * from movie where id=id
    reviews = Review.objects.filter(movie=id).order_by("-comment")

    average = reviews.aggregate(Avg("rating"))["rating__avg"]
    if average == None:
        average = 0
    average = round(average, 2)
    context = {"movie": movie, "reviews": reviews, "average": average}
    return render(request, "base/details.html", context)


# add movies to the database
def add_movies(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            if request.method == "POST":
                form = MovieForm(request.POST or None)

                # check if the form is valid
                if form.is_valid():
                    data = form.save(commit=False)
                    data.save()
                    return redirect("base:home")
            else:
                form = MovieForm()
            return render(
                request,
                "base/addmovies.html",
                {"form": form, "controller": "Add Movies"},
            )

        # if they are not admin
        else:
            return redirect("base:home")

    # if they are not loggedin
    return redirect("accounts:login")


# edit the movie
def edit_movies(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # get the movies linked with id
            movie = Movie.objects.get(id=id)

            # form check
            if request.method == "POST":
                form = MovieForm(request.POST or None, instance=movie)
                # check if form is valid
                if form.is_valid():
                    data = form.save(commit=False)
                    data.save()
                    return redirect("base:detail", id)
            else:
                form = MovieForm(instance=movie)
            return render(
                request,
                "base/addmovies.html",
                {"form": form, "controller": "Edit Movies"},
            )
        # if they are not admin
        else:
            return redirect("base:home")

    # if they are not loggedin
    return redirect("accounts:login")


# delete movies
def delete_movies(request, id):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            # get the moveis
            movie = Movie.objects.get(id=id)

            # delte the movie
            movie.delete()
            return redirect("base:home")
        # if they are not admin
        else:
            return redirect("base:home")

    # if they are not loggedin
    return redirect("accounts:login")


def add_review(request, id):
    if request.user.is_authenticated:
        movie = Movie.objects.get(id=id)
        if request.method == "POST":
            form = ReviewForm(request.POST or None)
            if form.is_valid():
                data = form.save(commit=False)
                data.comment = request.POST["comment"]
                data.rating = request.POST["rating"]
                data.user = request.user
                data.movie = movie
                data.save()
                return redirect("base:detail", id)
        else:
            form = ReviewForm()
        return render(request, "base/details.html", {"form": form})
    else:
        return redirect("accounts:login")


# edit the review
def edit_review(request, movie_id, review_id):
    if request.user.is_authenticated:
        movie = Movie.objects.get(id=movie_id)
        # review
        review = Review.objects.get(movie=movie, id=review_id)

        # check if the review was done by the logged in user
        if request.user == review.user:
            # grant permission
            if request.method == "POST":
                form = ReviewForm(request.POST, instance=review)
                if form.is_valid():
                    data = form.save(commit=False)
                    if (data.rating > 10) or (data.rating < 0):
                        error = (
                            "Out or range. Please select rating from 0 to 10."
                        )
                        return render(
                            request,
                            "base/editreview.html",
                            {"error": error, "form": form},
                        )
                    else:
                        data.save()
                        return redirect("base:detail", movie_id)
            else:
                form = ReviewForm(instance=review)
            return render(request, "base/editreview.html", {"form": form})
        else:
            return redirect("base:detail", movie_id)
    else:
        return redirect("accounts:login")


# delete reivew
def delete_review(request, movie_id, review_id):
    if request.user.is_authenticated:
        movie = Movie.objects.get(id=movie_id)
        # review
        review = Review.objects.get(movie=movie, id=review_id)

        # check if the review was done by the logged in user
        if request.user == review.user:
            # grant permission to delete
            review.delete()

        return redirect("base:detail", movie_id)

    else:
        return redirect("accounts:login")
