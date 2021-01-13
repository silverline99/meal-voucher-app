from django.urls import path

from . import views

urlpatterns = [
    path('add_employees/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('restore_warehouse/', views.restore_warehouse, name='restore_warehouse'),
    path('add_employees/', views.add_employees, name='add_employees'),
    path('remove_mealvouchers/', views.remove_mealvouchers, name='remove_mealvouchers'),
    path('add_mealvouchers/', views.add_mealvouchers, name='add_mealvouchers'),
    path('distribute_mealvouchers/', views.distribute_mealvouchers, name='distribute_mealvouchers'),
    path('', views.homepage, name='homepage'),
    ]
