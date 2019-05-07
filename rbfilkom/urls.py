from django.urls import path, re_path
from django.conf.urls import url, include
from . import views

urlpatterns =[
    path('', views.index, name='index'),
    path('login/', views.loginpage, name='login'),
    path('logout/', views.userlogout, name='logout'),
    path('HomeAdmin/', views.adminhome, name='adminHome'),
    path('DaftarKoleksi/', views.daftarkoleksi, name='daftarKoleksi'),
    path('TambahKoleksi/', views.tambahkoleksi, name= 'tambahKoleksi'),
    path('DaftarPeminjaman/', views.daftarpeminjaman, name='daftarPeminjaman'),
    path('DaftarPemesanan/', views.daftarpemesanan, name='daftarPemesanan'),
    path('DaftarAnggota/', views.daftaranggota, name='daftarAnggota'),
    path('DaftarDenda/', views.daftardenda, name='daftarDenda'),
    path('DaftarSkripsi/', views.daftarskripsi, name='daftarSkripsi'),
    path('DaftarAkunPengguna/', views.daftarakunpengguna, name='daftarAkunPengguna'),
    path('DaftarJenisKoleksi/', views.daftarjeniskoleksi, name='daftarJenisKoleksi'),
    path('TambahPeminjaman/', views.tambahpeminjaman, name='tambahPeminjaman'),
    path('TambahPemesanan/', views.tambahpemesanan, name='tambahPemesanan'),
    path('TambahJenisKoleksi/', views.tambahjeniskoleksi, name='tambahJenisKoleksi'),
    path('TambahTopikKoleksi/', views.tambahtopikkoleksi, name='tambahTopikKoleksi'),
    path('TambahSumberKoleksi/', views.tambahsumberkoleksi, name='tambahSumberKoleksi'),
    path('TambahBahasaKoleksi/', views.tambahbahasakoleksi, name='tambahBahasaKoleksi'),
    path('TambahAkunPengguna/', views.tambahakunpengguna, name='tambahAkunPengguna'),
    path('UbahKoleksi/', views.ubahkoleksi, name='ubahKoleksi'),
    path('UbahJenisKoleksi/', views.ubahjeniskoleksi, name='ubahJenisKoleksi'),
    path('UbahTopikKoleksi/', views.ubahtopikkoleksi, name='ubahTopikKoleksi'),
    path('UbahSumberKoleksi/', views.ubahsumberkoleksi, name='ubahSumberKoleksi'),
    path('UbahBahasaKoleksi/', views.ubahbahasakoleksi, name='ubahBahasaKoleksi'),
    path('UbahAkunPengguna/', views.ubahakunpengguna, name='ubahAkunPengguna'),
    path('CetakBarkode/', views.cetakbarkode, name='cetakBarkode'),
    path('RiwayatPinjaman/', views.riwayatpeminjaman, name='riwayatPeminjaman'),
    path('RiwayatPemesanan/', views.riwayatpemesanan, name='riwayatPemesanan'),
    path('MahasiswaHome/', views.mahasiswahome, name='mahasiswaHome'),
    path('Koleksi/', views.koleksi_mhs, name='koleksi_mahasiswa'),
    path('Registrasi/', views.registrasi, name='registrasi'),
    path('UploadKoleksi/', views.uploadkoleksi, name='uploadKoleksi'),
    path('Test/', views.listkoleksi, name='list'),
    path('TestCreate/', views.koleksi_create, name='createkoleksi'),
    path('ShowNotification/', views.show_notification, name='show_notification'),
    re_path(r'^Aktivasi/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.activate, name='activate'),
    re_path(r'^notificationread/(?P<notifikasi_id>\d+)/$', views.mark_as_read_notification, name='read_notification'),
    path('Feedback/', views.feedback, name='feedback'),
    path('Laporan/', views.laporan, name='laporan'),
    path('CetakLaporan/', views.cetaklaporan, name='cetaklaporan'),
    path('Skripsi', views.daftarskripsi, name='detilSkripsi'),
    re_path(r'^DataSkripsi/(?P<id>\w+)/$', views.abstrakskripsi, name='abstrak'),
    re_path(r'^Feedbacks/(?P<kode_pinjam>\w+)/$', views.feedbacks, name='feedbacks')
]





