from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q 
from .models import Listing, Seller
from .forms import ListingFilterForm

def listing_view(request):
    listings_list = Listing.objects.select_related('item', 'seller').order_by('-created_at')

    form = ListingFilterForm(request.GET)
    
    if form.is_valid():
        filters = Q()

        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        if min_price is not None:
            filters &= Q(price__gte=min_price)
        if max_price is not None:
            filters &= Q(price__lte=max_price)

        min_steam_level = form.cleaned_data.get('min_steam_level')
        max_steam_level = form.cleaned_data.get('max_steam_level')

        if min_steam_level is not None:
            filters &= Q(seller__steam_level__gte=min_steam_level)
        if max_steam_level is not None:
            filters &= Q(seller__steam_level__lte=max_steam_level)

        min_cs2_hours = form.cleaned_data.get('min_cs2_hours')
        max_cs2_hours = form.cleaned_data.get('max_cs2_hours')
        if min_cs2_hours is not None:
            filters &= Q(seller__cs2_hours__gte=min_cs2_hours)
        if max_cs2_hours is not None:
            filters &= Q(seller__cs2_hours__lte=max_cs2_hours)

        min_total_trades = form.cleaned_data.get('min_total_trades')
        max_total_trades = form.cleaned_data.get('max_total_trades')
        if min_total_trades is not None:
            filters &= Q(seller__total_trades__gte=min_total_trades)
        if max_total_trades is not None:
            filters &= Q(seller__total_trades__lte=max_total_trades)

        selected_country = form.cleaned_data.get('country')
        if selected_country:
            filters &= Q(seller__country=selected_country)
        
        search_username = form.cleaned_data.get('username')
        if search_username:
            filters &= Q(seller__username__icontains=search_username)
            
        listings_list = listings_list.filter(filters)

    paginator = Paginator(listings_list, 20)

    page = request.GET.get('page')
    try:
        listings = paginator.page(page)
    except PageNotAnInteger:
        listings = paginator.page(1)
    except EmptyPage:
        listings = paginator.page(paginator.num_pages)

    context = {
        'listings': listings,
        'form': form,
        'current_params': request.GET.copy(), 
    }
    if 'page' in context['current_params']:
        del context['current_params']['page']

    return render(request, 'scanner/listings.html', context)