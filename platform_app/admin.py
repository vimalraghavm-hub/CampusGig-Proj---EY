from django.contrib import admin
from .models import Category, Gig, Order, Message, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'price', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'gig', 'client', 'status', 'created_at')
    list_filter = ('status', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'created_at')
