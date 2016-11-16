import re
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import SuspiciousOperation
from .models import Upload, Title, Release, Link, Host, Upload_Host

# Create your views here.
def index(request):
  upload_list = Upload.objects.all().order_by('-pub_date')
  return render(request, 'track/index.html', {'upload_list': upload_list})

#
# Unauthorized
#
def unauthorized():
  return HttpResponseRedirect(reverse('track:index', args=()))

#
# Upload
#
def upload_view(request, upload_id):
  upload = get_object_or_404(Upload, pk=upload_id)
  return render(request, 'track/upload-view.html', {'upload': upload})

@login_required
def upload_edit_error(request, upload_id, error):
  titles_list = Title.objects.all().order_by('title_text')

  upload = None
  if upload_id != '0':
    upload = get_object_or_404(Upload, pk=upload_id)
    if not upload.can_modify(request):
      return unauthorized()

  return render(request, 'track/upload-edit.html', {'titles_list': titles_list,
                                                    'upload': upload,
                                                    'error_message': error})

@login_required
def upload_edit(request, upload_id):
  if not request.POST:
    return upload_edit_error(request, upload_id, '')

  if request.POST.get('title_id') == '0':
    return upload_edit_error(request, upload_id, "No hi ha cap anime seleccionat")

  if request.POST.get('release_id') == '':
    return upload_edit_error(request, upload_id, "No hi ha cap release seleccionada")

  links_str = request.POST.get('links').strip()
  if links_str == "":
    return upload_edit_error(request, upload_id, "Falta la llista d'enllaços")

  if upload_id != '0':
    u = get_object_or_404(Upload, pk=upload_id)
    if not u.can_modify(request):
      return unauthorized()
    u.upload_text = request.POST.get('upload_text')
    u.release_id = request.POST.get('release_id')
  else:
    u = Upload(upload_text = request.POST.get('upload_text'),
               release_id = request.POST.get('release_id'),
               user_id = request.user.id,
               pub_date = timezone.now()
              )
  u.save()

  upload_link_save(u, request.POST.get('links'))

  return HttpResponseRedirect(reverse('track:upload-view', args=(u.id,)))

@login_required
def upload_delete(request, upload_id):
  try:
    upload = get_object_or_404(Upload, pk=upload_id)
    if not upload.can_modify(request):
      return unauthorized()
  except:
    return HttpResponseRedirect(reverse('track:index', args=()))
  if 'sure' in request.GET:
    title_id = upload.release.title.id
    upload.delete()
    return HttpResponseRedirect(reverse('track:title-view', args=(title_id,)))
  return render(request, 'track/upload-delete.html', {'upload': upload})

@login_required
def upload_link_save(upload, links_text):
  def nl_protocol(protocol):
    return "\n" + protocol.group(0).lower()

  from django.db import IntegrityError
  from zlib import crc32

  link_crc32 = crc32(re.sub(r'([\n\r\t ]|\<.*)', '', links_text).encode())

  if upload.link_crc32 != link_crc32:
    upload.pub_date = timezone.now()
    upload.link_crc32 = link_crc32

  upload.link_set.all().delete()
  upload.upload_host_set.all().delete()

  host_list = []
  links_text = re.sub(r'((?<!\n)(ed2k|http|https|ftp)://|magnet:\?)', nl_protocol, links_text, flags=re.IGNORECASE)
  links = re.compile(r'(\w[^\<\n]+)\<?(.+)?').findall(links_text)
  for link, title in links:
    if title.strip() == "": title = link
    l = Link(link_url = link.strip(),
             link_text = title.strip()[:200],
             upload_id = upload.id)

    l.host_id = l.get_host()
    if l.host_id not in host_list:
      try:
        Host(hostname = l.host_id).save(force_insert = True)
      except IntegrityError:
        pass
    l.save()
    if l.host_id not in host_list:
      Upload_Host(upload_id = upload.id, host_id = l.host_id).save()
      host_list.append(l.host_id)

  host_list.sort()
  upload.host_list = ', '.join(host_list)

  upload.save()

@login_required
def upload_raw(request, upload_id):
  link_list = get_object_or_404(Upload, pk=upload_id).link_set.values_list('link_url', flat=True)
  return HttpResponse("\n".join(link_list), content_type='text/plain')

#
# Title
#
def title_list(request):
  return render(request, 'track/title-list.html', {'title_list': Title.objects.all().order_by('title_text')});

def title_view(request, title_id):
  title = get_object_or_404(Title, pk=title_id)
  return render(request, 'track/title-view.html', {'title': title})

@login_required
def title_edit_error(request, title_id, error):
  title = None
  if title_id != '0':
    title = get_object_or_404(Title, pk=title_id)
    if not title.can_modify(request):
      return unauthorized()
  return render(request, 'track/title-edit.html', {'title': title, 'error_message': error})

@login_required
def title_edit(request, title_id):
  if not request.POST:
    return title_edit_error(request, title_id, '')

  if request.POST.get('title_text').strip() == '':
    return title_edit_error(request, title_id, "El títol no pot estar buit")

  if request.POST.get('cover_url').strip() == '':
    return title_edit_error(request, title_id, "Heu d'asociar una imatge de portada")

  if title_id != '0':
    t = get_object_or_404(Title, pk=title_id)
    if not t.can_modify(request):
      return unauthorized()
    t.title_text = request.POST.get('title_text').strip()
    t.summary_text = request.POST.get('summary_text').strip()
    t.year_start = request.POST.get('year_start') or 0
    t.year_end = request.POST.get('year_end') or 0
    t.episodes = request.POST.get('episodes') or 0
    t.runtime_minutes = request.POST.get('runtime_minutes') or 0
    t.cover_url = request.POST.get('cover_url').strip()
  else:
    t = Title(title_text = request.POST.get('title_text').strip(),
              summary_text = request.POST.get('summary_text').strip(),
              year_start = request.POST.get('year_start') or 0,
              year_end = request.POST.get('year_end') or 0,
              episodes = request.POST.get('episodes') or 0,
              runtime_minutes = request.POST.get('runtime_minutes') or 0,
              cover_url = request.POST.get('cover_url').strip(),
             )

  if request.POST.get('status') is not None:
    t.status = request.POST.get('status')

  t.save()

  return HttpResponseRedirect(reverse('track:title-view', args=(t.id,)))

@login_required
def title_delete(request, title_id):
  try:
    if not request.user.is_staff:
      return unauthorized()
    title = get_object_or_404(Title, pk=title_id)
  except:
    return HttpResponseRedirect(reverse('track:index', args=()))
  if 'sure' in request.GET:
    title.delete()
    return HttpResponseRedirect(reverse('track:title-list', args=()))
  return render(request, 'track/title-delete.html', {'title': title})

#
# Release
#
@login_required
def release_edit_error(request, title_id, release_id, error):
  release = None

  if release_id != '0':
    release = get_object_or_404(Release, pk=release_id)
    if not release.can_modify(request):
      return unauthorized()

  title = get_object_or_404(Title, pk=title_id)
  return render(request, 'track/release-edit.html', {'title': title, 'release': release, 'error_message': error})

@login_required
def release_edit(request, title_id, release_id):
  if not request.POST:
    return release_edit_error(request, title_id, release_id, '')

  if request.POST.get('release_text').strip() == '':
    return release_edit_error(request, title_id, release_id, "Falta un comentari breu de la release")

  if request.POST.get('video_text').strip() == '':
    return release_edit_error(request, title_id, release_id, "Heu d'introduir la informació del vídeo")

  if request.POST.get('audio_text').strip() == '':
    return release_edit_error(request, title_id, release_id, "Heu d'introduir la informació del àudio")

  if release_id == '0':
    links_str = request.POST.get('links').strip()
    if links_str == "":
      return release_edit_error(request, title_id, release_id, "Falta la llista d'enllaços")

  if release_id != '0':
    r = get_object_or_404(Release, pk=release_id)
    if not r.can_modify(request):
      return unauthorized()
    r.release_text = request.POST.get('release_text').strip()
    r.video_text = request.POST.get('video_text').strip()
    r.audio_text = request.POST.get('audio_text').strip()
    r.subs_text = request.POST.get('subs_text').strip()
  else:
    r = Release(release_text = request.POST.get('release_text').strip(),
              video_text = request.POST.get('video_text').strip(),
              audio_text = request.POST.get('audio_text').strip(),
              subs_text = request.POST.get('subs_text').strip(),
              title_id = title_id,
              user_id = request.user.id,
              pub_date = timezone.now()
             )
  r.save()

  if request.POST.get('links', '') != '':
    if release_id == '0':
      u = Upload(release_id = r.id, user_id = r.user.id, pub_date = r.pub_date)
      u.save()
    else:
      u = r.upload_set.first()
    u.upload_text = request.POST.get('upload_text')
    upload_link_save(u, request.POST.get('links'))

  return HttpResponseRedirect(reverse('track:title-view', args=(title_id,)))

@login_required
def release_delete(request, title_id, release_id):
  try:
    release = get_object_or_404(Release, pk=release_id)
    if not release.can_modify(request):
      return unauthorized()
  except:
    return HttpResponseRedirect(reverse('track:index', args=()))
  if 'sure' in request.GET:
    release.delete()
    return HttpResponseRedirect(reverse('track:title-view', args=(title_id,)))
  return render(request, 'track/release-delete.html', {'release': release})

@login_required
def release_upload(request, title_id, release_id):
  titles_list = Title.objects.all().order_by('title_text')
  select_title_id = int(title_id);
  select_release_id = int(release_id);
  return render(request, 'track/upload-edit.html', {'titles_list': titles_list,
                                                    'title_id': select_title_id,
                                                    'release_id': select_release_id,
                                                   })

def release_get_options(request):
  release_list = Release.objects.filter(title_id=request.GET['title_id']).order_by('-pub_date')
  return render(request, 'track/release-get-options.html', {'release_list': release_list})
