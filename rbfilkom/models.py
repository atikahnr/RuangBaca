from django.db import models
from django.contrib.auth.models import User
import datetime


def pemesanan_increment():
    last_booking = TransaksiPemesanan.objects.all().last()
    if not last_booking:
        return 'RBFB' + '00001'
    booking_id = last_booking.kode_pesan
    booking_int = int(booking_id[4:9])
    new_booking_int = booking_int + 1
    new_booking_id = 'RBFB' + str(new_booking_int).zfill(5)
    return new_booking_id


def peminjaman_increment():
    last_booking = TransaksiPeminjaman.objects.all().last()
    print(last_booking)
    if not last_booking:
        return 'RBFO' + '00001'
    booking_id = last_booking.kode_pinjam
    booking_int = int(booking_id[4:9])
    new_booking_int = booking_int + 1
    new_booking_id = 'RBFO' + str(new_booking_int).zfill(5)
    return new_booking_id


class JenisKoleksi(models.Model):
    kode_koleksi = models.CharField(primary_key=True, max_length=50, blank=False, null=False)
    nama_jenis_koleksi = models.CharField(max_length=200, blank=False)


class BahasaKoleksi(models.Model):
    kode_bahasa = models.CharField(primary_key=True, max_length=50)
    nama_bahasa_koleksi = models.CharField(max_length=200, blank=False)


class TopikKoleksi(models.Model):
    kode_topik = models.CharField(primary_key=True, max_length=50)
    nama_topik_koleksi = models.CharField(max_length=200, blank=False)


class SumberKoleksi(models.Model):
    kode_sumber = models.CharField(primary_key=True, max_length=50)
    nama_sumber_koleksi = models.CharField(max_length=200, blank=False)


class Koleksi(models.Model):
    kode_eksamplar = models.CharField(primary_key=True, max_length=30)
    isbn_issn = models.CharField(max_length=50, blank=False, null=False)
    no_panggil = models.CharField(max_length=50, blank=False, null=False)
    judul = models.CharField(max_length=200, blank=False)
    pengarang = models.CharField(max_length=200, blank=False)
    penerbit = models.CharField(max_length=200, blank=False)
    tahun_terbit = models.CharField(max_length=200, blank=False)
    tempat_terbit = models.CharField(max_length=200, blank=False)
    jenis_koleksi = models.ForeignKey(JenisKoleksi, blank=False, on_delete=models.CASCADE)
    sumber_koleksi = models.ForeignKey(SumberKoleksi, blank=False, on_delete=models.CASCADE)
    topik_koleksi = models.ForeignKey(TopikKoleksi, blank=False, on_delete=models.CASCADE)
    bahasa_koleksi =models.ForeignKey(BahasaKoleksi, blank=False, on_delete=models.CASCADE)
    status_ketersediaan = models.IntegerField(blank=False, null=False)
    gambar = models.ImageField("Image", upload_to='files/', null=True, blank=True, default='static/img/empty.png')


class Mahasiswa(models.Model):
    nim = models.CharField(primary_key=True, max_length=200)
    nama_mahasiswa = models.CharField(max_length=200, blank=False)
    alamat_mahasiswa = models.CharField(max_length=200, blank=False)
    no_telp = models.CharField(max_length=200, blank=False)
    email_mahasiswa = models.CharField(max_length=200, blank=False)
    Angkatan = models.CharField(max_length=200, blank=False)
    jurusan = models.CharField(max_length=200, blank=False)
    prodi = models.CharField(max_length=200, blank=False)
    status_mahasiswa = models.CharField(max_length=200, blank=False)
    status_tanggungan = models.IntegerField(blank=False, null=False)


class TransaksiPeminjaman(models.Model):
    kode_pinjam = models.CharField(primary_key=True, default=peminjaman_increment, editable=False, max_length=50)
    kode_eksamplar = models.ForeignKey(Koleksi, on_delete=models.CASCADE)
    tanggal_pinjam = models.DateField()
    tanggal_kembali = models.DateField()
    status_peminjaman = models.IntegerField(blank=True, null=True)
    nim = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)


class TransaksiPemesanan(models.Model):
    kode_pesan = models.CharField(primary_key=True, default=pemesanan_increment, editable=False, max_length=50)
    kode_eksamplar = models.ForeignKey(Koleksi, on_delete=models.CASCADE)
    tanggal_pesan = models.DateField()
    status_pemesanan = models.IntegerField(blank=False, null=False)
    nim = models.ForeignKey(Mahasiswa, on_delete=models.CASCADE)
    antrian = models.IntegerField(blank=False, null=False, default=0)
    tenggat_waktu = models.DateField(default=datetime.datetime.today())


class AkunPengguna(models.Model):
    username = models.CharField(primary_key=True, max_length=50)
    password = models.CharField(max_length=50, blank=False)
    tipe_pengguna = models.CharField(max_length=50, blank=False)
    nama_pengguna = models.CharField(max_length=50, blank=False)


class Denda(models.Model):
    kode_transaksi = models.OneToOneField(TransaksiPeminjaman, blank=False, related_name='has', on_delete=models.CASCADE)
    status_denda = models.CharField(max_length=100, blank=False, null=False)


class Skripsi(models.Model):
    nim = models.ForeignKey(Mahasiswa, blank=False, related_name='has', on_delete=models.CASCADE)
    nama_mahasiswa = models.CharField(max_length=200, blank=False)
    jurusan = models.CharField(max_length=200, blank=False)
    prodi = models.CharField(max_length=200, blank=False)
    judul_skripsi = models.CharField(max_length=200, blank=False)
    status_skripsi = models.CharField(max_length=200, blank=False)
    dosen_pembiming = models.CharField(max_length=200, blank=False)
    abstrak = models.FileField(upload_to='abstrak/', blank=True)


class Notifikasi(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Mahasiswa, blank=False, related_name='get', on_delete=models.CASCADE)
    viewed = models.BooleanField(default=False)
    message = models.CharField(max_length=200, blank=False)
    kode_pinjam = models.ForeignKey(TransaksiPeminjaman, blank=True, default=None, related_name='sent', on_delete=models.CASCADE)
    kode_pesan = models.ForeignKey(TransaksiPemesanan, blank=True, null=True, default=None, related_name='sent', on_delete=models.CASCADE)


class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    rating = models.IntegerField(blank=False, null=False, default=0)
    message = models.TextField(blank=True, default="-")
    kode_pinjam = models.ForeignKey(TransaksiPeminjaman, blank=True, default=None, related_name='give', on_delete=models.CASCADE)
    kode_pesan = models.ForeignKey(TransaksiPemesanan, blank=True, null=True, default=None, related_name='give', on_delete=models.CASCADE)


class StaticVariable(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.BooleanField()