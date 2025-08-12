from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import openai, requests
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.hashers import make_password
from .models import *
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import WebsiteSerializer
import os

openai.api_key = os.environ.get('API_KEY')
# https://console.groq.com/keys
openai.api_base = "https://api.groq.com/openai/v1"

User = get_user_model()

class WebsiteAPIView(APIView):
    """
    A single API view for full CRUD on Website model.
    """
    def get(self, request, pk=None):
        if pk:
            website = get_object_or_404(Website, pk=pk)
            serializer = WebsiteSerializer(website)
            return Response(serializer.data)
        else:
            websites = Website.objects.all().order_by('-created_at')
            serializer = WebsiteSerializer(websites, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = WebsiteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        website = get_object_or_404(Website, pk=pk)
        serializer = WebsiteSerializer(website, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        website = get_object_or_404(Website, pk=pk)
        website.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
def valide_token(request):
    token = request.session.get('jwt_token')
    if not token:
        return redirect('login')
    try:
        JWTAuthentication().get_validated_token(token)
    except:
        return redirect('login')

    return

def register_view(request):
    if request.method == 'POST':
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        role = Role.objects.get(name=role)
        if User.objects.filter(username=username).exists():
            return render(request, 'builder/register.html', {'error': 'Username already taken'})
        User.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            role=role
        )
        return redirect('login')
    return render(request, 'builder/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('view_website')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        response = requests.post(
            request.build_absolute_uri('/api/token/'),
            json={'username': email, 'password': password},
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            token_data = response.json()
            request.session['jwt_token'] = token_data['access']
        if user is not None:
            login(request, user)
            return redirect('view_website')
        else:
            return render(request, 'builder/login.html', {'error': 'Invalid credentials'})
    return render(request, 'builder/login.html')

@login_required
def generate_form_view(request):
    valide_token(request)
    if request.method == 'POST':
        business = request.POST.get('business')
        industry = request.POST.get('industry')

        prompt = f"Generate content for a website for a business called '{business}' in the '{industry}' industry. Include hero section, about us, and at-least 3 services list."

        response = openai.ChatCompletion.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response['choices'][0]['message']['content']

        content_json = {
            "raw": content
        }
        data = {
            'title': business,
            'industry': industry,
            'content_json':content_json,
                }
        if request.POST.get('id'):
            id = request.POST.get('id')
            url = request.build_absolute_uri(f'/api/websites/{id}/')
            response = requests.patch(
                url,
                json=data,
                headers={
                    'Authorization': f"Bearer {request.session.get('jwt_token')}",
                    'Content-Type': 'application/json'
                }
            )
            return redirect('view_website')
        else:
            data['owner']=request.user.id
            url = request.build_absolute_uri('/api/websites/')
            response = requests.post(
            url,
            json=data,
            headers={
                'Authorization': f"Bearer {request.session.get('jwt_token')}",
                'Content-Type': 'application/json'
            }
        )
        return redirect('view_website')

    return render(request, 'builder/generate_form.html')

@login_required
def view_website(request):
    if not request.user.is_authenticated:
        return redirect('login')
    valide_token(request)
    url = request.build_absolute_uri(f'/api/websites/')
    response = requests.get(
        url,
        headers={
            'Authorization': f"Bearer {request.session.get('jwt_token')}",
            'Content-Type': 'application/json',
        }
    )
    if response.status_code == 200:
        website_data = response.json()
    else:
        website_data = {}

    return render(request, 'builder/generate_result.html', {
        'websites': website_data,
    })

@login_required
def edit_website(request, website_id):
    valide_token(request)
    website = get_object_or_404(Website, id=website_id)

    return render(request, 'builder/generate_form.html', {
        'business': website.title,
        'industry': website.industry,
        'id':website.id,
    })

@login_required
def delete_website(request, website_id):
    valide_token(request)
    url = request.build_absolute_uri(f'/api/websites/{website_id}/')
    requests.delete(
        url,
        headers={
            'Authorization': f"Bearer {request.session.get('jwt_token')}",
            'Content-Type': 'application/json',
        }
    )
    return redirect('view_website')

@login_required
def logout_view(request):
    request.session.flush()
    return redirect('login')