from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Notification


@login_required
def liste_notifications(request):
    notifications = Notification.objects.filter(destinataire=request.user)
    non_lues      = notifications.filter(lu=False).count()

    # Marquer toutes comme lues si demandé
    if request.GET.get('tout_lire'):
        notifications.filter(lu=False).update(lu=True)
        return redirect('notifications:liste')

    context = {
        'notifications': notifications[:50],
        'non_lues'     : non_lues,
    }
    return render(request, 'notifications/liste.html', context)


@login_required
def marquer_lue(request, pk):
    notif = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    notif.lu = True
    notif.save()
    if notif.lien:
        return redirect(notif.lien)
    return redirect('notifications:liste')


@login_required
def supprimer_notification(request, pk):
    notif = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    notif.delete()
    return redirect('notifications:liste')


@login_required
def api_non_lues(request):
    """API JSON pour le badge de la navbar."""
    count = Notification.objects.filter(
        destinataire=request.user, lu=False
    ).count()
    return JsonResponse({'count': count})