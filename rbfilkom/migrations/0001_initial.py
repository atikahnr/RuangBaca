# Generated by Django 2.1b1 on 2018-12-13 08:51

from django.db import migrations, models
import django.db.models.deletion
import rbfilkom.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AkunPengguna',
            fields=[
                ('username', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=50)),
                ('tipe_pengguna', models.CharField(max_length=50)),
                ('nama_pengguna', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='BahasaKoleksi',
            fields=[
                ('kode_bahasa', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('nama_bahasa_koleksi', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Denda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jenis_denda', models.CharField(max_length=100)),
                ('nominal_denda', models.IntegerField()),
                ('status_denda', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='JenisKoleksi',
            fields=[
                ('kode_koleksi', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('nama_jenis_koleksi', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Koleksi',
            fields=[
                ('kode_eksamplar', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('isbn_issn', models.CharField(max_length=50)),
                ('no_panggil', models.CharField(max_length=50)),
                ('judul', models.CharField(max_length=200)),
                ('pengarang', models.CharField(max_length=200)),
                ('penerbit', models.CharField(max_length=200)),
                ('tahun_terbit', models.CharField(max_length=200)),
                ('tempat_terbit', models.CharField(max_length=200)),
                ('status_ketersediaan', models.IntegerField()),
                ('gambar', models.ImageField(blank=True, null=True, upload_to='files/', verbose_name='Image')),
                ('bahasa_koleksi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbfilkom.BahasaKoleksi')),
                ('jenis_koleksi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbfilkom.JenisKoleksi')),
            ],
        ),
        migrations.CreateModel(
            name='Mahasiswa',
            fields=[
                ('nim', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('nama_mahasiswa', models.CharField(max_length=200)),
                ('alamat_mahasiswa', models.CharField(max_length=200)),
                ('no_telp', models.CharField(max_length=200)),
                ('email_mahasiswa', models.CharField(max_length=200)),
                ('password', models.CharField(max_length=200)),
                ('jurusan', models.CharField(max_length=200)),
                ('prodi', models.CharField(max_length=200)),
                ('status_mahasiswa', models.CharField(max_length=200)),
                ('status_tanggungan', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Skripsi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_mahasiswa', models.CharField(max_length=200)),
                ('jurusan', models.CharField(max_length=200)),
                ('prodi', models.CharField(max_length=200)),
                ('judul_skripsi', models.CharField(max_length=200)),
                ('status_skripsi', models.CharField(max_length=200)),
                ('dosen_pembiming', models.CharField(max_length=200)),
                ('nim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='has', to='rbfilkom.Mahasiswa')),
            ],
        ),
        migrations.CreateModel(
            name='SumberKoleksi',
            fields=[
                ('kode_sumber', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('nama_sumber_koleksi', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TopikKoleksi',
            fields=[
                ('kode_topik', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('nama_topik_koleksi', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TransaksiPemesanan',
            fields=[
                ('kode_pesan', models.CharField(default=rbfilkom.models.pemesanan_increment, editable=False, max_length=50, primary_key=True, serialize=False)),
                ('tanggal_pesan', models.DateField()),
                ('status_pemesanan', models.IntegerField()),
                ('kode_eksamplar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbfilkom.Koleksi')),
                ('nim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbfilkom.Mahasiswa')),
            ],
        ),
        migrations.CreateModel(
            name='TransaksiPeminjaman',
            fields=[
                ('kode_pinjam', models.CharField(default=rbfilkom.models.peminjaman_increment, editable=False, max_length=50, primary_key=True, serialize=False)),
                ('tanggal_pinjam', models.DateField()),
                ('tanggal_kembali', models.DateField()),
                ('status_peminjaman', models.IntegerField(blank=True, null=True)),
                ('kode_eksamplar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbfilkom.Koleksi')),
                ('nim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbfilkom.Mahasiswa')),
            ],
        ),
        migrations.AddField(
            model_name='koleksi',
            name='sumber_koleksi',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbfilkom.SumberKoleksi'),
        ),
        migrations.AddField(
            model_name='koleksi',
            name='topik_koleksi',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbfilkom.TopikKoleksi'),
        ),
        migrations.AddField(
            model_name='denda',
            name='kode_transaksi',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='has', to='rbfilkom.TransaksiPeminjaman'),
        ),
    ]