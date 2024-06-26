from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as loginAuth, logout as logoutAuth
from django.contrib.admin.views.decorators import staff_member_required 
from historico.views import adicionar_historico, remover_historico, atualiza_historico

@staff_member_required(login_url='/auth/login')
def listar_usuarios(request):
  usuarios = User.objects.all()
  return render(request, 'usuarios.html', {'usuarios': usuarios})

def atualizar_usuario(request, usuario_id):
   user = User.objects.filter(id=usuario_id).first() 
   
   if request.method == 'POST':
      userAntigo = User.objects.filter(id=usuario_id).first() 
      
      check = request.POST.get('admin') == 'on' if True else False
      user.username = request.POST.get('username')
      user.first_name = request.POST.get('primeiroNome')
      user.last_name = request.POST.get('sobrenome')
      if request.POST.get('senha'):        
        user.set_password(request.POST.get('senha'))
        
      user.email = request.POST.get('email')
      user.is_staff = check
      user.save()
      
      if request.user.username == '':
        atualiza_historico(user.username, 'Usuário', user, userAntigo)
      else:
        atualiza_historico(request.user, 'Usuário', user, userAntigo)
      
      if request.user.is_staff:
        usuarios = User.objects.all()
        return redirect('/auth/usuarios', {'usuarios': usuarios})
      
      loginAuth(request, user)  
      return redirect('/')
      
   else:
      return render(request, 'cadastro.html', {'usuario': user})

def excluir_usuario(request, usuario_id):
  user = User.objects.filter(id=usuario_id).first() 
  user.delete()
  remover_historico(request.user.username, 'Usuário', usuario_id)
  
  usuarios = User.objects.all()
  return render(request, 'usuarios.html', {'usuarios': usuarios})

def cadastro(request):
  if request.method == 'GET':
    return render(request, 'cadastro.html')
  else:
    username = request.POST.get('username')
    primeiroNome = request.POST.get('primeiroNome')
    sobrenome = request.POST.get('sobrenome')
    email = request.POST.get('email')
    senha = request.POST.get('senha')
    check = request.POST.get('admin') == 'on' if True else False
    user = User.objects.filter(username=username, email=email).first()
    
    if user:
      user = ()
      return render(request, 'cadastro.html')
    else:      
      user = User.objects.create_user(username=username, email=email, password=senha, first_name=primeiroNome, last_name=sobrenome, is_staff=check)
      user.save()
      
      if request.user.username != username:
        adicionar_historico(request.user.username, 'Usuário', user.id)
        usuarios = User.objects.all()
        return render(request, 'usuarios.html', {'usuarios': usuarios})
      
      adicionar_historico(user.username, 'Usuário', user.id)
      return render(request, 'login.html')
    
def login(request):
  if request.method == 'GET':
    return render(request, 'login.html')
  else:
    username = request.POST.get('username')
    senha = request.POST.get('senha')
    
    user = authenticate(request, username=username, password=senha)
    
    if user is not None:
      loginAuth(request, user)  
      
      return redirect('/')
    else:
      return render(request, 'login.html', {'error': 'E-mail ou Senha invalidos'})
    
def logout(request):
  logoutAuth(request)
  return redirect('/')