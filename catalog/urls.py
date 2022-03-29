from unicodedata import name
from xml.etree.ElementInclude import include
from django.urls import URLPattern, path
from . import views
from django.urls import include
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('',views.index,name='index'),
    path('books/',views.BookListView.as_view(),name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(),name='book-detail'),
    path('authors/',views.AuthorListView.as_view(),name='author'),
    path('author/<int:pk>',views.AuthorDetailView.as_view(),name='author-detail'),
    path('mybooks/',views.LoanedBooksByUserListView.as_view(),name='my-borrowed'),
    path('borrowed/',views.AllBorrowedBooksByUserListView.as_view(),name='all-borrowed'),
    path('book/<uuid:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
    path('author/create/',views.AuthorCreate.as_view(),name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
    path('book/create/',views.BookCreate.as_view(),name='book-create'),
    path('book/<int:pk>/update/',views.BookUpdate.as_view(),name='book-update'),
    path('book/<int:pk>/delete/',views.BookDelete.as_view(),name='book-update'),
    path('image_upload/',views.plant_img_upload,name='image-upload'),
    #path('success', views.success, name = 'success'),
    path('uploaded_images', views.display_plant_images, name='uploaded-images'),
    path('login/',views.LoginPage,name='login'),
    path('logout/',views.logoutUser,name='logout'),
    path('register/',views.register, name='register')
]

