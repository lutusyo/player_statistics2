from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.staticfiles import finders
from django.conf import settings
from xhtml2pdf import pisa
import os
from django.shortcuts import get_object_or_404
from matches_app.models import Match, Team


def link_callback(uri, rel):
    """
    Convert URIs to absolute system paths for xhtml2pdf.
    Works in both local and production environments.
    """
    # Try using Django's staticfiles finder
    result = finders.find(uri)
    if result:
        if isinstance(result, (list, tuple)):
            result = result[0]
        return os.path.realpath(result)

    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    path = None

    # Handle MEDIA
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))

    # Handle STATIC
    elif uri.startswith(sUrl):
        # First try production root
        path = os.path.join(sRoot, uri.replace(sUrl, ""))

        # ✅ If STATIC_ROOT doesn't exist locally, fallback to STATICFILES_DIRS
        if not os.path.exists(path) or not os.path.isfile(path):
            for static_dir in settings.STATICFILES_DIRS:
                alt_path = os.path.join(static_dir, uri.replace(sUrl, ""))
                if os.path.exists(alt_path):
                    path = alt_path
                    break

    else:
        return uri  # Leave external URLs untouched

    # Final sanity check
    if not path or not os.path.isfile(path):
        raise FileNotFoundError(f"Cannot find file: {uri}")

    return os.path.realpath(path)




def download_full_report(request, match_id, our_team_id):
    match = get_object_or_404(Match, id=match_id)
    our_team = get_object_or_404(Team, id=our_team_id)

    template_path = 'tagging_app/output/full_report.html'
    context = {
        'match_id': match_id,
        'our_team_id': our_team_id,
        "match": match,
        "our_team": our_team,
    }

    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="match_report_{match_id}.pdf"'

    pisa_status = pisa.CreatePDF(
        html,
        dest=response,
        link_callback=link_callback,
    )

    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response
