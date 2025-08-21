import requests
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse

def activate_user_template_view(request, uid, token):
    activation_url = f"http://ittissal.com/api/auth/users/activation/"
    data = {"uid": uid, "token": token}
    response = requests.post(activation_url, data=data)

    if response.status_code == 204:
        return render(request, "activation_success.html")
    else:
        return render(request, "activation_failed.html")


class ResetPasswordView(View):
    def get(self, request, uid, token):
        # Show the reset form
        return render(request, "reset_password.html", {"uid": uid, "token": token})

    def post(self, request, uid, token):
        new_password = request.POST.get("new_password")
        re_password = request.POST.get("re_password")

        if new_password != re_password:
            return render(request, "reset_password.html", {
                "uid": uid,
                "token": token,
                "error": "Passwords do not match"
            })

        # Call Djoser's reset_password_confirm endpoint
        response = requests.post(
            "http://ittissal.com/api/auth/users/reset_password_confirm/",
            json={"uid": uid, "token": token, "new_password": new_password},
        )

        if response.status_code == 204:  # success
            return render(request, "reset_success.html")
        else:
            return render(request, "reset_error.html")
