from .models import TransaksiPeminjaman, Denda, Notifikasi, Mahasiswa
import datetime
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.template.loader import render_to_string


def denda():
    obj = TransaksiPeminjaman.objects.filter(status_peminjaman=1)
    for i in obj:
        is_denda = Denda.objects.filter(kode_transaksi=i.kode_pinjam).last()
        if is_denda is None:
            delta = datetime.date.today() - i.tanggal_kembali
            if delta.days >= 1:
                denda = Denda(
                    kode_transaksi=TransaksiPeminjaman.objects.filter(kode_pinjam=i.kode_pinjam).last(),
                    status_denda="Aktif"
                )
                denda.save()
                #create new notification
                mhs_nimm = TransaksiPeminjaman.objects.values_list("nim", flat=True).get(kode_pinjam=i.kode_pinjam)
                mhs = Mahasiswa.objects.filter(nim=mhs_nimm).last()
                notif = Notifikasi(user=mhs,
                                   message='sudah lewat dari tanggal pengembalian yang ditentukan, silahkan mengurus pengembalian buku dan pelunasan denda.',
                                   kode_pinjam=TransaksiPeminjaman.objects.filter(kode_pinjam=i.kode_pinjam).last())
                notif.save()
                #send email notification
                user = User.objects.filter(username=mhs_nimm).last()
                mail_subject = 'Pemberitahuan Denda'
                message = render_to_string('emailNotifikasi.html', {
                    'user': user
                })
                to_email = str(User.objects.values_list("email", flat=True).get(username=mhs_nimm))
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()