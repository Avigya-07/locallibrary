from mailbox import FormatError
import re
from django.forms import Form
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User # Required to assign User as a borrower
from django.shortcuts import get_object_or_404, render
from catalog.forms import RenewBookForm
from urllib import response
from django.test import TestCase
from django.urls import reverse
from catalog.models import Author
from django.contrib.auth.models import Permission

class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_authors=13

        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christan {author_id}',
                last_name=f'Surname {author_id}'
                )
                
    def test_url_exists_at_desired_location(self):
        response=self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_url_accessible_by_name(self):
        response= self.client.get(reverse('author'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response= self.client.get(reverse('author'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_list.html')
    
    # def test_pagination_is_five(self):
    #     response = self.client.get(reverse('author'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue('is_paginated' in response.context)
    #     self.assertTrue(response.context['is_paginated'] == True)
    #     self.assertEqual(len(response.context['author_list']),5)
    
import datetime

from django.utils import timezone
from django.contrib.auth.models import User # Required to assign User as a borrower

from catalog.models import BookInstance, Book, Genre, Language

class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
            language=test_language,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy%5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response=self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response,'/accounts/login/?next=/catalog/mybooks/')
    ########
    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login=self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response=self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']),'testuser1')
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']),0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status='o'
            book.save()
        response=self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']),'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('bookinstance_list' in response.context) 

        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual(bookitem.status, 'o')

    def test_pages_ordered_by_due_date(self):
        for book in BookInstance.objects.all():
            book.status='o'
            book.save()

        login = self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
            # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
            # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['bookinstance_list']),5)
        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back

from catalog.forms import RenewBookForm

import uuid
 # Required to grant the permission needed to set a book as returned.
##########
from catalog.forms import RenewBookForm
from django import forms
from django.contrib.auth.decorators import permission_required

@permission_required("can_mark_returned")
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        book_renewal_form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if forms.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = forms.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        book_renewal_form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'book_renewal_form': book_renewal_form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)



               