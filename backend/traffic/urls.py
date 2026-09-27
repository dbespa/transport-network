from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('locations/', views.location_handler, name='locations'),
    path('locations/create/', views.location_handler, name='location_create'),
    path('locations/<int:pk>/', views.location_handler, name='location_detail'),
    path('locations/<int:pk>/update/', views.location_handler, name='location_update'),
    path('locations/<int:pk>/delete/', views.location_handler, name='location_delete'),

    path('roads/', views.road_handler, name='roads'),
    path('roads/create/', views.road_handler, name='road_create'),
    path('roads/<int:pk>/', views.road_handler, name='road_detail'),
    path('roads/<int:pk>/update/', views.road_handler, name='road_update'),
    path('roads/<int:pk>/delete/', views.road_handler, name='road_delete'),

    path('contypes/', views.contype_handler, name='contypes'),
    path('contypes/create/', views.contype_handler, name='contype_create'),
    path('contypes/<int:pk>/', views.contype_handler, name='contype_detail'),
    path('contypes/<int:pk>/update/', views.contype_handler, name='contype_update'),
    path('contypes/<int:pk>/delete/', views.contype_handler, name='contype_delete'),

    path('traffic/', views.traffic_handler, name='traffic'),
    path('traffic/create/', views.traffic_handler, name='traffic_create'),
    path('traffic/<int:pk>/', views.traffic_handler, name='traffic_detail'),
    path('traffic/<int:pk>/update/', views.traffic_handler, name='traffic_update'),
    path('traffic/<int:pk>/delete/', views.traffic_handler, name='traffic_delete'),

    path('api/locations/', views.api_locations, name='api_locations'),
    path('api/roads/', views.api_roads, name='api_roads'),
    path('api/contypes/', views.api_contypes, name='api_contypes'),
    path('api/traffic/', views.api_traffic, name='api_traffic'),
    path('api/graph/', views.graph_api, name='api_graph'),
    path('api/current_weights/', views.current_weights, name='api_cur_weights'),
    path('api/weights_since/', views.weights_since, name = 'api_weights_since'),
    path('api/randomize_congestion/', views.randomize_congestion_api, name='api_randomize_congestion'),
    path('api/set_all_free/', views.set_all_free_api, name='api_set_all_free'),
    path('api/set_congestion_by_time/', views.set_congestion_by_time_of_day, name='api_set_congestion_by_time'),
    path('api/point/<int:point_id>/edges/', views.get_edges_for_point, name='api_edges'),
]