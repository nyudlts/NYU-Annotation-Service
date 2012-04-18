# Create your views here.
from django.contrib.admin.views.decorators import staff_member_required
from models import Book
from django.views.generic.simple import direct_to_template
from forms import CreateBookFromUriForm


