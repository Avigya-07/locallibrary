from ast import Num
from audioop import reverse
from dataclasses import fields
from multiprocessing import context
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Author, Book, BookInstance, Genre
import datetime
from catalog.models import BookInstance
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
from catalog.models import Author
from .forms import *
from PIL import ImageFilter
from django.contrib.auth import login, authenticate, logout 
from django.contrib import messages
from .forms import NewUserForm

@login_required(login_url='login')
def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books=Book.objects.all().count()
    num_instances=BookInstance.objects.all().count()

    #get available books
    num_instances_available=BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_author=Author.objects.count()

    #sessions : num of times visited
    num_visits=request.session.get('num_visits',0)
    request.session['num_visits']=num_visits +1

    #count for genre and books that contain a specific word
    genre_word=Genre.objects.filter(name__icontains='Fiction').count
    book_genre=Book.objects.filter(genre__name__icontains='finance').count()

    context={
        'num_books': num_books,
        'num_instances':num_instances,
        'num_instances_available':num_instances_available,
        'num_author':num_author,
        'genre_word':genre_word,
        'book_genre':book_genre,
        'num_visits':num_visits,
    }
    return render(request,'index.html',context=context)

class BookListView(LoginRequiredMixin,generic.ListView):
    login_url='login'
    model=Book
    paginate_by = 5

class BookDetailView(LoginRequiredMixin,generic.DetailView):
    model=Book
    login_url='login'

class AuthorListView(LoginRequiredMixin,generic.ListView):
    model=Author
    login_url='login'

class AuthorDetailView(LoginRequiredMixin,generic.DetailView):
    model=Author
    login_url='login'

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model=BookInstance
    template_name='catalog/bookinstance_list_borrowed_user.html'
    paginate_by=5
    login_url='login'

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class AllBorrowedBooksByUserListView(PermissionRequiredMixin,generic.ListView):
    model=BookInstance
    permission_required='can_mark_returned'
    template_name='catalog/bookinstance_all_borrowed_books.html'
    

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from catalog.forms import RenewBookForm

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)

class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
       data = self.cleaned_data['due_back']

       # Check if a date is not in the past.
       if data < datetime.date.today():
           raise ValidationError('Invalid date - renewal in past')

       # Check if a date is in the allowed range (+4 weeks from today).
       if data > datetime.date.today() + datetime.timedelta(weeks=4):
           raise ValidationError(('Invalid date - renewal more than 4 weeks ahead'))

       # Remember to always return the cleaned data.
       return data

    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': ('Renewal date')}
        help_texts = {'due_back': ('Enter a date between now and 4 weeks (default 3).')}

class AuthorCreate(PermissionRequiredMixin,CreateView):
    model=Author
    fields=['first_name', 'last_name','date_of_birth','date_of_death']
    initial= {'date_of_death': '11/06/2020'}
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(UpdateView):
    model=Author
    fields='__all__'    

class AuthorDelete(DeleteView):
    model=Author
    success_url = reverse_lazy('author')

class BookCreate(PermissionRequiredMixin,CreateView):
    model=Book
    fields='__all__'
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(UpdateView):
    model=Book
    fields='__all__'

class BookDelete(DeleteView):
    model=Book
    success_url = reverse_lazy('books')

#for image upload-test
def plant_img_upload(request):
    if request.method =='POST':
        form=plantForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('uploaded-images')
    else:
        form=plantForm()
        context={
            'form':form
        }
        return render(request, 'plant_upload.html' ,context)

def display_plant_images(request):
    if request.method == 'GET':
        plants=plant.objects.all() 
        context={
             'plants':plants,
        
        }
        return render(request,'display_plants.html',context)

def register(request):
    form=NewUserForm()

    if request.method == "POST":
        form=NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            user=form.cleaned_data.get('username')
            messages.success(request,'Account was created for:'+user)
            return redirect('login')
    return render(request=request, template_name="catalog/register.html", context={"form":form})

def LoginPage(request):
    if request.method =="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.info(request,'Username OR Password is incorrect')
            return render(request,'catalog/login.html', {})       
    context={}  
    return render(request,'catalog/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

