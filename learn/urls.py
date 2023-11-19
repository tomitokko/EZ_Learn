from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('video-resources', views.video_resources, name='video-resources'),
    path('pdf-resources', views.pdf_resources, name='pdf-resources'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('video-details', views.video_details, name='video-details'),
    path('pdf-details', views.pdf_details, name='pdf-details'),
    path('chatbot-response/', views.chatbot_response, name='chatbot-response'),
    path('convert-to-srt', views.convert_to_srt, name='convert-to-srt'),
    path('convert-pdf-text-to-speech', views.convert_pdf_text_to_speech, name='convert-pdf-text-to-speech')

]