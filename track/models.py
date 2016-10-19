import re
from django.db import models
from datetime import datetime
from django.contrib.auth.models import User as AuthUser

# Create your models here.
class Title(models.Model):
  title_text = models.CharField(max_length=200)
  summary_text = models.CharField(max_length=2000)
  year_start = models.IntegerField()
  year_end = models.IntegerField(blank=True, null=True)
  episodes = models.IntegerField()
  runtime_minutes = models.IntegerField()
  cover_url = models.CharField(max_length=200)
  status = models.SmallIntegerField(default=0)
  #
  def __str__(self):
    return self.title_text;
  #
  def get_release_list(self):
    return self.release_set.all().order_by('-pub_date')
  #
  def can_modify(self, request):
    return request.user.is_staff or self.status == 0

class User(models.Model):
  avatar_url = models.CharField(max_length=200)
  auth = models.ForeignKey(AuthUser, on_delete=models.PROTECT)

class Release(models.Model):
  title = models.ForeignKey(Title, on_delete=models.PROTECT)
  release_text = models.CharField(max_length=200)
  user = models.ForeignKey(AuthUser, on_delete=models.PROTECT)
  video_text = models.CharField(max_length=200)
  audio_text = models.CharField(max_length=200)
  subs_text = models.CharField(max_length=200)
  pub_date = models.DateTimeField('date published')
  #
  def __str__(self):
    return self.release_text;
  #
  def get_upload_list(self):
    return self.upload_set.all().order_by('-pub_date')
  #
  def can_modify(self, request):
    return request.user.is_staff or self.user.id == request.user.id

class Upload(models.Model):
  release = models.ForeignKey(Release, on_delete=models.CASCADE)
  user = models.ForeignKey(AuthUser, on_delete=models.PROTECT)
  upload_text = models.CharField(max_length=200)
  host_list = models.CharField(max_length=200, default='')
  link_crc32 = models.BigIntegerField(default=0)
  pub_date = models.DateTimeField(default=datetime.now)
  #
  def __str__(self):
    return self.upload_text;
  #
  def get_host_list(self):
    values = self.link_set.order_by('host').distinct().values_list('host', flat=True)
    return ', '.join(values);
  #
  def get_upload_host_ordered(self):
    return self.upload_host_set.order_by('host')
  #
  def can_modify(self, request):
    return request.user.is_staff or self.user.id == request.user.id

class Host(models.Model):
  hostname = models.CharField(max_length=100, primary_key=True)
  image = models.CharField(max_length=100, default='default.png')
  #
  def __str__(self):
    return self.hostname;

class Upload_Host(models.Model):
  upload = models.ForeignKey(Upload, on_delete=models.CASCADE)
  host = models.ForeignKey(Host, on_delete=models.PROTECT)

class Link(models.Model):
  upload = models.ForeignKey(Upload, on_delete=models.CASCADE)
  link_url = models.CharField(max_length=2000)
  link_text = models.CharField(max_length=200)
  host = models.ForeignKey(Host, on_delete=models.PROTECT)
  #
  def __str__(self):
    return self.link_text;
  #
  def get_host(self):
    if self.link_url[:7] == 'magnet:':
      return 'torrent'
    elif self.link_url[:5] == 'ed2k:':
      return 'ed2k'
    elif self.link_url[-8:] == '.torrent':
      return 'torrent'
    else:
      match = re.findall(r'(?:^[a-z0-9]+\:\/\/)([^\/]+)', self.link_url, flags=re.IGNORECASE)
      if len(match) > 0: return match[0].lower()
      else: return self.link_url

  #
  def get_link_line(self):
    if self.link_text == self.link_url:
      return self.link_url
    return self.link_url +"<"+ self.link_text
