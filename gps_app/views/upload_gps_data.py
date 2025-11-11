from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from gps_app.forms import GPSUploadForm
from gps_app.utils.import_gps_data import import_gps_data
from matches_app.models import Match
import tempfile

def upload_gps_csv(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == "POST":
        form = GPSUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']

            # Save temporary file to disk
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                for chunk in csv_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name

            # Import data
            import_gps_data(tmp_path, match_id)

            messages.success(request, "GPS data uploaded successfully!")
            return redirect('gps_app:gps_upload', match_id=match.id)  # <- fixed

    else:
        form = GPSUploadForm()

    return render(request, "gps_app/upload_csv.html", {"form": form, "match": match})
