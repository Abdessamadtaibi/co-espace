import requests
from django.shortcuts import render

def activate_user_template_view(request, uid, token):
    activation_url = f"http://ittissal.com/api/auth/users/activation/"
    data = {"uid": uid, "token": token}
    response = requests.post(activation_url, data=data)

    if response.status_code == 204:
        return render(request, "activation_success.html")
    else:
        return render(request, "activation_failed.html")
