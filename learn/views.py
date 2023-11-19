from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
import pprint
from .models import Profile
from pytube import YouTube
import os
import assemblyai as aai
from django.conf import settings
import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from youtube_transcript_api import YouTubeTranscriptApi
# from googletrans import Translator, LANGUAGES
from translate import Translator
from textblob import TextBlob
import deepl
from pathlib import Path
from pydub import AudioSegment, silence
from gtts import gTTS
import srt
from django.core.files.storage import default_storage
from io import BytesIO
import json
from django.core.files.storage import FileSystemStorage






# Create your views here.
LANGUAGE_CHOICES = [
    ('mandarin', 'Mandarin'),  # The most spoken language in the world
    ('spanish', 'Spanish'),    # Second most spoken language by number of native speakers
    ('english', 'English'),    # The most international and third most spoken language by native speakers
    ('hindi', 'Hindi'),        # One of the most spoken languages in India
    ('bengali', 'Bengali'),    # Widely spoken in Bangladesh and parts of India
    ('portuguese', 'Portuguese'),  # Official language of Portugal, Brazil, and some African countries
    ('russian', 'Russian'),    # Most widely spoken language in Eurasia
    ('japanese', 'Japanese'),  # Official language of Japan
    ('punjabi', 'Punjabi'),    # Widely spoken in Pakistan and India
    ('marathi', 'Marathi'),    # One of the major languages of India
    ('telugu', 'Telugu'),      # One of the major languages in South India
    ('wu', 'Wu (Shanghainese)'),  # Spoken in parts of China
    ('turkish', 'Turkish'),    # Official language of Turkey
    ('korean', 'Korean'),      # Official language of North and South Korea
    ('french', 'French'),      # Official language in France and various other countries
    ('german', 'German'),      # Widely spoken in Germany, Austria, and parts of Switzerland
    ('vietnamese', 'Vietnamese'),  # Official language of Vietnam
    ('tamil', 'Tamil'),        # Spoken in parts of India, Sri Lanka, and Singapore
    ('yue', 'Yue (Cantonese)'),   # Spoken in parts of China, especially Hong Kong and Macau
    ('urdu', 'Urdu')           # One of the official languages of Pakistan and India
]

COUNTRY_CHOICES = [
    ('china', 'China'),
    ('india', 'India'),
    ('united_states', 'United States'),
    ('indonesia', 'Indonesia'),
    ('pakistan', 'Pakistan'),
    ('brazil', 'Brazil'),
    ('nigeria', 'Nigeria'),
    ('bangladesh', 'Bangladesh'),
    ('russia', 'Russia'),
    ('mexico', 'Mexico'),
    ('japan', 'Japan'),
    ('ethiopia', 'Ethiopia'),
    ('philippines', 'Philippines'),
    ('egypt', 'Egypt'),
    ('vietnam', 'Vietnam'),
    ('congo', 'Congo (DRC)'),
    ('turkey', 'Turkey'),
    ('iran', 'Iran'),
    ('germany', 'Germany'),
    ('thailand', 'Thailand')
]

def video_search(search_term):
    url = "https://learning-objects-v2.p.rapidapi.com/search"

    querystring = {"keywords":search_term,"lang":"en","type":"video","sort":"popularity","model":"strict","max":"10","page":"0"}

    headers = {
        "X-RapidAPI-Key": "21d322268amsh4b1c363def79a1fp14c18djsn859b6f259e07",
        "X-RapidAPI-Host": "learning-objects-v2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    # pprint.pprint(response.json())
    return response.json()

def pdf_search(search_term):
    url = "https://getbooksinfo.p.rapidapi.com/"

    querystring = {"s":"poor dad rich dad"}

    headers = {
    	"X-RapidAPI-Key": "21d322268amsh4b1c363def79a1fp14c18djsn859b6f259e07",
    	"X-RapidAPI-Host": "getbooksinfo.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)


    # pprint.pprint(response.json())
    return response.json()


def index(request):
    
    return render(request, 'index.html')

def video_resources(request):
    if request.method == 'POST':
        search_term = request.POST['search_term']
        search_results = video_search(search_term)
        extracted_info = []

        for content in search_results['response']['content']:
            item_info = {
                "Picture": content.get('picture', 'N/A'),
                "Provider": content.get('provider', 'N/A'),
                "Title": content.get('title', 'N/A'),
                "Type": content.get('type', ['N/A'])[0],  # Assuming type is a list with at least one item
                "URL": content.get('url', 'N/A'),
                "Owner": content.get('author', [{'name': 'N/A'}])[0]['name'],  # Assuming author is a list with at least one item with a name
                "Description": content.get('description', 'N/A')
            }
            extracted_info.append(item_info)

        context = {
            'extracted_info': extracted_info,
        }

        return render(request, 'video-resource.html', context)
    else:
        return render(request, 'video-resource.html')
    


def download_audio(link):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=settings.MEDIA_ROOT)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    os.rename(out_file, new_file)
    return new_file

# def get_transcription(link):
#     audio_file = download_audio(link)
#     audio_file_name = os.path.basename(audio_file)
#     full_audio_link = 'http://127.0.0.1:8000/media/'+audio_file_name
#     print(full_audio_link)
#     aai.settings.api_key = "7b9d45faa00b4563a2a3683b2cdc66b8"

#     transcriber = aai.Transcriber()
#     transcript = transcriber.transcribe(full_audio_link)
#     print('heyyyyy')
#     print(transcript.text)   
#     return transcript.text

def get_transcription(link):

    import whisper

    audio_file = download_audio(link)

    model = whisper.load_model("base")
    result = model.transcribe(audio_file)
    print(result["text"])
    return result["text"]

def srt_to_audio(srt_file, output_file_name):
    with open(srt_file, 'r') as file:
        subtitles = list(srt.parse(file.read()))

    combined_audio = AudioSegment.empty()
    last_end = 0  # Track the end time of the last subtitle

    for subtitle in subtitles:
        # Calculate silence based on the time since the end of the last subtitle
        silence_duration = max(0, subtitle.start.total_seconds() * 1000 - last_end)
        silence_segment = AudioSegment.silent(duration=silence_duration)

        # Generate speech for the current subtitle
        tts_buffer = BytesIO()
        tts = gTTS(text=subtitle.content, lang='en')
        tts.write_to_fp(tts_buffer)
        tts_buffer.seek(0)
        speech_segment = AudioSegment.from_file(tts_buffer, format="mp3")

        # Combine silence and speech
        combined_audio += silence_segment + speech_segment
        last_end = subtitle.end.total_seconds() * 1000

    # Save the combined audio
    audio_file_path = os.path.join('media', output_file_name)
    combined_audio.export(audio_file_path, format="mp3")

    return audio_file_path

def convert_to_srt(request):
    youtube_id = request.POST['youtube_id']
    title = request.POST['title']
    description = request.POST['description']
    youtube_link = request.POST['youtube_link']
    language = request.POST['language']
    filename = youtube_id+".srt"

    transcript = YouTubeTranscriptApi.get_transcript(youtube_id)
    srt_format = ""
    counter = 1

    for segment in transcript:
        start_time = segment['start']
        end_time = start_time + segment['duration']
        start_time_formatted = f"{int(start_time // 3600):02d}:{int((start_time % 3600) // 60):02d}:{int(start_time % 60):02d},{int((start_time % 1) * 1000):03d}"
        end_time_formatted = f"{int(end_time // 3600):02d}:{int((end_time % 3600) // 60):02d}:{int(end_time % 60):02d},{int((end_time % 1) * 1000):03d}"

        srt_format += f"{counter}\n{start_time_formatted} --> {end_time_formatted}\n{segment['text']}\n\n"
        counter += 1

    srt_transcript = srt_format.strip()

    translator = deepl.Translator("edb048c1-9c7f-7116-2e27-11b90aa8a602:fx")

    translated_content = []
    for line in srt_transcript.split('\n'):
        # Check if the line is a text to be translated
        if line and not line.strip().isdigit() and '-->' not in line:
            result = translator.translate_text(line, target_lang=language)
            translated_content.append(result.text)
        else:
            translated_content.append(line)

    new_srt_language = '\n'.join(translated_content)

    # print(str(new_srt_language.translate(to="es")))

    srt_directory = os.path.join(settings.MEDIA_ROOT, 'subtitles')
    os.makedirs(srt_directory, exist_ok=True)

    # Path for the new SRT file
    file_path = os.path.join(srt_directory, filename)

    # Write the SRT content to the file
    with open(file_path, 'w') as file:
        file.write(new_srt_language)

    dubbed_audio_file = srt_to_audio(file_path, youtube_id+".mp3")
    print(dubbed_audio_file)   
    return redirect('/video-details?dubbed_audio='+ dubbed_audio_file +'&title='+ title +'&link='+ youtube_link +'&description='+ description )
    # return(file_path)
    # return file_path



@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        user_input = request.POST.get('message')
        transcript = request.POST.get('transcript')  # Load this appropriately

        openai.api_key = settings.OPENAI_API_KEY

        try:
            response = openai.Completion.create(
                model="text-davinci-003",  # or any other suitable model
                prompt=f"{transcript}\n\nQ: {user_input}\nA:",
                temperature=0.7,
                max_tokens=150
            )
            return JsonResponse({'message': response.choices[0].text.strip()})
        except Exception as e:
            return JsonResponse({'message': str(e)})

    return JsonResponse({'message': 'Invalid request'}, status=400)

def video_details(request):
    title = request.GET.get('title')
    link = request.GET.get('link')
    link_id = link[-11:]
    description = request.GET.get('description')
    video_transcript = get_transcription(link)


    context = {
        'title': title,
        'link': link,
        'link_id': link_id,
        'description': description,
        'video_transcript': video_transcript,
    }

    return render(request, 'video-details.html', context)
   

def pdf_resources(request):
    if request.method == 'POST':
        search_term = request.POST['search_term']
        search_results = pdf_search(search_term)
        extracted_info = []

        # for content in search_results['response']['content']:
        #     item_info = {
        #         "Picture": content.get('picture', 'N/A'),
        #         "Provider": content.get('provider', 'N/A'),
        #         "Title": content.get('title', 'N/A'),
        #         "Type": content.get('type', ['N/A'])[0],  # Assuming type is a list with at least one item
        #         "URL": content.get('url', 'N/A'),
        #         "Owner": content.get('author', [{'name': 'N/A'}])[0]['name'],  # Assuming author is a list with at least one item with a name
        #         "Description": content.get('description', 'N/A')
        #     }
        #     extracted_info.append(item_info)

        for result in search_results['results']:
            item_info = {
                "title" : result.get('title', 'No Title'),
                "img_link" : result.get('img_link', 'No Image Link'),
                "pdf_link" : result.get('pdf_link', 'No PDF Link'),
            }

            extracted_info.append(item_info)
        print(extracted_info)

        context = {
            'extracted_info': extracted_info,
        }
        return render(request, 'pdf-resources.html', context)
    else:
        return render(request, 'pdf-resources.html')

def pdf_details(request):
    title = request.GET.get('title')
    link = request.GET.get('link')


    context = {
        'title': title,
        'link': link,
    }

    return render(request, 'pdf-details.html', context)

def convert_pdf_text_to_speech(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        text = data.get('text', '')
        print(text)

        if text:
            # Convert the text to speech
            tts = gTTS(text=text, lang='en')
            fs = FileSystemStorage()
            
            # Save the audio file
            file_name = 'speech.mp3'
            with fs.open(file_name, 'wb') as audio_file:
                tts.write_to_fp(audio_file)
            audio_url = fs.url(file_name)
            print(audio_url)
            return JsonResponse({'audio_url': audio_url})
        else:
            return JsonResponse({'error': 'No text provided'}, status=400)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def signup(request):
    context = {
        'LANGUAGE_CHOICES': LANGUAGE_CHOICES,
        'COUNTRY_CHOICES': COUNTRY_CHOICES,
    }

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        country = request.POST['country']
        language = request.POST['language']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password, last_name=last_name, first_name=first_name)
                user.save()

                new_profile = Profile(owner_user=user, country=country, language=language)
                new_profile.save() 

                #log user in and redirect to home page
                user_login = auth.authenticate(username=username, password=password)
                # do that later where you take care of the context thing
                auth.login(request, user_login)
                return redirect('/')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        # return render(request, 'signup.html', context)
    else:
        return render(request, 'signup.html', context)

def login(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None:
                auth.login(request, user)
                return redirect('/')
            else:
                messages.info(request, 'Credentials Invalid')
                return redirect('login')

        else:
            return render(request, 'login.html')
        
def logout(request):
    auth.logout(request)
    return redirect('login')