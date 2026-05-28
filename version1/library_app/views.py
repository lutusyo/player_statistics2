from django.shortcuts import render, redirect, get_object_or_404

from version1.tagging_app.models import AttemptToGoal
from .models import Highlight, HighlightClip, Reel
import os
import imageio_ffmpeg




def add_to_highlight(request, clip_id):

    clip = get_object_or_404(AttemptToGoal, id=clip_id)

    if request.method == 'POST':

        action = request.POST.get('action')

        # CREATE NEW
        if action == 'create':

            name = request.POST.get('new_name')

            highlight = Highlight.objects.create(name=name)

        # SELECT EXISTING
        else:
            highlight_id = request.POST.get('highlight_id')

            highlight = Highlight.objects.get(id=highlight_id)

        HighlightClip.objects.create(highlight=highlight, clip=clip, order=highlight.clips.count())

        return redirect(request.META.get('HTTP_REFERER'))

    highlights = Highlight.objects.all()

    context = {
            'clip': clip,
            'highlights': highlights
        }

    return render(request, 'library_app/add_to_highlight.html', context)


def library_home(request):
    return render(request, 'library_app/library_home.html')

def highlights_list(request):

    highlights = Highlight.objects.all()

    context = {
            'highlights': highlights
        }

    return render(request, 'library_app/highlights_list.html', context)


def view_highlight(request, highlight_id):

    highlight = get_object_or_404(Highlight, id=highlight_id)
    clips = highlight.clips.all()

    context = {
            'highlight': highlight,
            'clips': clips
        }

    return render( request, 'library_app/view_highlight.html', context )



def generate_reel(request, highlight_id):
    highlight = get_object_or_404(Highlight, id=highlight_id)
    clips = highlight.clips.all()

    context = {
            'highlight': highlight,
            'clips': clips
        }

    return render(request, 'library_app/generate_reel.html', context)






import os
import imageio_ffmpeg

os.environ["IMAGEIO_FFMPEG_EXE"] = imageio_ffmpeg.get_ffmpeg_exe()
from moviepy import VideoFileClip, concatenate_videoclips

def create_reel(highlight):

    video_clips = []

    for hc in highlight.clips.all():

        if hc.clip.video_clip:

            path = hc.clip.video_clip.path

            if os.path.exists(path):

                clip = VideoFileClip(path)

                video_clips.append(clip)

    if not video_clips:
        return None

    final_video = concatenate_videoclips(
        video_clips,
        method="compose"
    )

    reels_dir = os.path.join('media', 'reels')

    os.makedirs(reels_dir, exist_ok=True)

    output_path = os.path.join(
        reels_dir,
        f'{highlight.name}.mp4'
    )

    final_video.write_videofile(
        output_path,
        codec='libx264'
    )

    return output_path






from django.core.files import File

def generate_reel_action(request, highlight_id):

    highlight = Highlight.objects.get(id=highlight_id)

    output_path = create_reel(highlight)

    if not output_path:
        return redirect('library_app:highlights_list')

    reel = Reel.objects.create(
        highlight=highlight,
        title=highlight.name,
        is_generated=True
    )

    with open(output_path, 'rb') as f:

        reel.video_file.save(
            f'{highlight.name}.mp4',
            File(f)
        )

    highlight.status = 'generated'
    highlight.save()

    return redirect('library_app:reels_list')




def reels_list(request):

    reels = Reel.objects.all()

    return render(
        request,
        'library_app/reels_list.html',
        {
            'reels': reels
        }
    )


def delete_highlight(request, highlight_id):

    highlight = get_object_or_404(
        Highlight,
        id=highlight_id
    )

    highlight.delete()

    return redirect('library_app:highlights_list')