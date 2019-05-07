from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import User, Group
from django.contrib import messages
from rbfilkom.models import *
from .forms import *
from django.core.files.storage import FileSystemStorage
from datetime import timedelta
from django.contrib.auth.decorators import login_required
import datetime, requests, xlrd
import urllib.error, urllib.request, barcode
from barcode.writer import ImageWriter
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, HttpResponseBadRequest,HttpResponseServerError
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from os.path import join, dirname, abspath
from django.db.models.functions import TruncMonth, TruncYear
from django.db.models import Count, Sum
from .static.fusioncharts import FusionCharts
from .kodeEksamplar import get_kode_eksamplar, kode_eksamplar


def registrasi(request):
    message_Reg = None
    if request.method == 'POST':
        try:
            mhs_nim = str(request.POST.get("nim", ""))
            urllib.request.urlopen('http://127.0.0.1:8800/mhs/?status_mahasiswa=Aktif')
            response = requests.get('http://127.0.0.1:8800/mhs/?status_mahasiswa=Aktif&nim={0}'.format(mhs_nim))
            mhs = response.json()
            if mhs:
                a = User(
                    first_name="mahasiswa",
                    username=str(request.POST.get("nim", "")),
                    password=str(request.POST.get("password", "")),
                    email=str(request.POST.get("email", "")),
                    is_superuser=False,
                    is_staff=False,
                    is_active=False
                    )
                a.save()
                a_id = User.objects.all().last()
                a_group = Group.objects.get(name="mahasiswa")
                a_group.user_set.add(a_id)
                a.is_active = False
                a.save()
                print(mhs[0]['nim'][:3])
                mahasiswa = Mahasiswa(
                    nim=mhs[0]['nim'],
                    nama_mahasiswa=mhs[0]['nama_mahasiswa'],
                    alamat_mahasiswa=mhs[0]['alamat_mahasiswa'],
                    no_telp=mhs[0]['no_telp'],
                    email_mahasiswa=mhs[0]['email_mahasiswa'],
                    jurusan=mhs[0]['jurusan'],
                    prodi=mhs[0]['prodi'],
                    status_tanggungan=mhs[0]['status_tanggungan'],
                    status_mahasiswa=1,
                    Angkatan=get_angkatan(mhs[0]['nim'][:3])
                )
                mahasiswa.save()
                current_site = get_current_site(request)
                mail_subject = 'Aktivasi akun Ruang Baca FILKOM'
                message = render_to_string('emailAktivasi.html', {
                    'user': a,
                    'domain': current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(a.pk)).decode(),
                    'token':account_activation_token.make_token(a),
                })
                to_email = str(request.POST.get("email"))
                email = EmailMessage(
                    mail_subject, message, to=[to_email]
                )
                email.send()
                message_Reg = 'Please confirm your email address to complete the registration'
            else:
                messages.error(request, 'NIM yang dimasukkan tidak terdaftar')
        except urllib.error.HTTPError:
            print('fail')
        except urllib.error.URLError:
            print('url error')
            messages.error(request, 'Mahasiswa Server is not Active yet')
    return render(request, 'registrasi.html', {'message': message_Reg})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login to your account.')
    else:
        return HttpResponse('Activation link is invalid!')


def index(request):
    return render(request, 'index.html')


def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None and user.is_active:
            request.session.set_expiry(86400)
            login(request, user)
            if user.groups.filter(name='mahasiswa').exists():
                return redirect(mahasiswahome)
            else:
                return redirect(daftarkoleksi)
        else:
            messages.error(request, 'username or password not correct')
            return render(request, 'login.html')
    else:
        pass
    return render(request, 'login.html')


def userlogout(request):
    logout(request)
    return redirect(index)


def get_notifikasi_mhs(request):
    mhs_username = request.user
    print(mhs_username)
    mhs = Mahasiswa.objects.filter(nim=mhs_username).last()
    print(mhs)
    n = Notifikasi.objects.filter(user=mhs, viewed=False)
    pinjam = TransaksiPeminjaman.objects.filter(nim=mhs).order_by('status_peminjaman')
    pesan = TransaksiPemesanan.objects.filter(nim=mhs).order_by('status_pemesanan')
    obj = {'notifikasi': n, 'pinjam': pinjam, 'pesan': pesan}
    return obj


@login_required
def mahasiswahome(request):
    mhs_username = request.user
    print(mhs_username)
    mhs = Mahasiswa.objects.filter(nim=mhs_username).last()
    print(mhs)
    n = Notifikasi.objects.filter(user=mhs, viewed=False)
    count_n = n.count()
    print(count_n)
    pinjam = TransaksiPeminjaman.objects.filter(nim=mhs).order_by('status_peminjaman')
    pesan = TransaksiPemesanan.objects.filter(nim=mhs).order_by('status_pemesanan')
    return render(request, 'daftarTransaksi.html', {'notifikasi': n,
                                                    'pinjam': pinjam,
                                                    'pesan': pesan,
                                                    'count': count_n})


@login_required
def adminhome(request):
    print(request.user)
    data = TransaksiPeminjaman.objects.all()
    user = User.objects.all()
    return render_to_response('adminHome.html', {'kode_pinjam': data, 'username': user})


@login_required
def show_notification(request):
    obj = get_notifikasi_mhs(request)
    mhs_username = request.user
    mhs = Mahasiswa.objects.filter(nim=mhs_username).last()
    n = Notifikasi.objects.filter(user=mhs).order_by('viewed')
    messages = None
    return render(request, 'notificationpage.html', {'id': n, 'message': messages}, obj)


def feedbacks(request, kode_pinjam):
    if request.POST['form-type'] == 'feedback_forms':
        kj = kode_pinjam
        feedback = Feedback.objects.filter(kode_pinjam=kj)
        if feedback:
            mhs_username = request.user
            print(mhs_username)
            mhs = Mahasiswa.objects.filter(nim=mhs_username).last()
            print(mhs)
            n = Notifikasi.objects.filter(user=mhs).order_by('viewed')
            messages = "message"
            return render_to_response('notificationpage.html', {'messages': messages, 'id': n})
        else:
            m = request.POST.get("messages")
            print(m)
            obj = Feedback(
                rating=int(request.POST.get("star", "")),
                message=str(request.POST.get("messages", "")),
                kode_pinjam=TransaksiPeminjaman.objects.filter(kode_pinjam=kj).last()
            )
            obj.save()
        return redirect(show_notification)
    else:
        return render(request, 'notificationpage.html')


def mark_as_read_notification(request, notifikasi_id):
    n = Notifikasi.objects.get(id=notifikasi_id)
    n.viewed = True
    n.save()
    return HttpResponseRedirect('/rbfilkom/ShowNotification/')


@login_required
def feedback(request):
    if request.method == 'POST':
        print(request.POST['form-type'])
        if request.POST['form-type'] == 'notifikasi_forms':
            kode_pinjam = str(request.POST.get("kode_pinjam", ""))
            feedback = Feedback.objects.filter(kode_pinjam=kode_pinjam)
            if feedback:
                mhs_username = request.user
                print(mhs_username)
                mhs = Mahasiswa.objects.filter(nim=mhs_username).last()
                print(mhs)
                n = Notifikasi.objects.filter(user=mhs).order_by('viewed')
                messages = "heyhaloo"
                return render_to_response('notificationpage.html', {'messages': messages, 'id':n})
            else:
                return render(request, 'feedbackForm.html', {"kode_pinjam": kode_pinjam})
        elif request.POST['form-type'] == 'feedback_forms':
            kode_pinjam = str(request.POST.get("kode_pinjam", ""))
            obj = Feedback(
                rating=int(request.POST.get("star", "")),
                message=str(request.POST.get("messages", "")),
                kode_pinjam=TransaksiPeminjaman.objects.filter(kode_pinjam=kode_pinjam).last()
            )
            obj.save()
            return redirect(show_notification)
    return redirect(show_notification)


#Manajemen Koleksi
@login_required
def daftarkoleksi(request):
    get_koleksi = Koleksi.objects.all()
    get_tk = TopikKoleksi.objects.all()
    get_bk = BahasaKoleksi.objects.all()
    obj = {
        "kode_eksamplar": get_koleksi
    }
    if request.method == 'POST':
        if request.POST['form-type'] == u"koleksi_forms":
            if 'change' in request.POST:
                get_koleksi_id = request.POST.get("kode_eksamplar", "")
                print(get_koleksi_id)
                get_koleksi = Koleksi.objects.filter(kode_eksamplar=get_koleksi_id)
                obj = {
                    "kode_eksamplar": get_koleksi,
                    "kode_topik": get_tk,
                    "kode_bahasa": get_bk
                }
                return render(request, 'ubahKoleksi.html', obj)
            elif 'delete' in request.POST:
                get_koleksi_id = request.POST.get("kode_eksamplar", "")
                get_koleksi = Koleksi.objects.filter(kode_eksamplar=get_koleksi_id)
                get_koleksi.delete()
    return render(request, 'daftarKoleksi.html', obj)


@login_required
def koleksi_mhs(request):
    get_koleksi = Koleksi.objects.all()
    get_tk = TopikKoleksi.objects.all()
    get_bk = BahasaKoleksi.objects.all()
    obj = {
        "kode_eksamplar": get_koleksi
    }
    return render(request, 'koleksi.html', obj)


def listkoleksi(request):
    koleksi = Koleksi.objects.all()
    return render(request, 'listkoleksi.html', {'kode_eksamplar':koleksi})


def koleksi_create(request):
    print('create')
    form = KoleksiForm()
    context = {'form': form}
    html_form = render_to_string('partial_book_create.html',
                                 context,
                                 request=request,
                                 )
    return JsonResponse({'html_form': html_form})


def koleksi_update(request, pk):
    print('update')
    koleksi = get_object_or_404(Koleksi, pk=pk)
    if request.method == 'POST':
        form = KoleksiForm(request.POST, instance=koleksi)
    else:
        form = KoleksiForm(instance=koleksi)
    return koleksi_create(request, form, 'partial_book_update.html')


@login_required
def tambahkoleksi(request):
    get_jk = JenisKoleksi.objects.all()
    get_sk = SumberKoleksi.objects.all()
    get_tk = TopikKoleksi.objects.all()
    get_bk = BahasaKoleksi.objects.all()
    if request.method == 'POST':
        jk = str(request.POST.get("jenis_kol"))
        sk = str(request.POST.get("sumber_kol"))
        thn = str(request.POST.get("tahun_inv"))[2:4]
        no = str(request.POST.get("no_inv"))
        filepath = request.FILES.get("file_gambar", False)
        print(filepath)
        if filepath is False:
            tpk = str(request.POST.get("topik_koleksi"))
            bhs = str(request.POST.get("bahasa_koleksi"))
            obj = Koleksi(
                kode_eksamplar=get_kode_eksamplar(jk, sk, thn, no),
                isbn_issn=str(request.POST.get("isbn_issn", "")),
                no_panggil=str(request.POST.get("no_panggil", "")),
                judul=str(request.POST.get("judul_koleksi", "")),
                pengarang=str(request.POST.get("pengarang", "")),
                penerbit=str(request.POST.get("penerbit", "")),
                tahun_terbit=str(request.POST.get("tahun_terbit", "")),
                tempat_terbit=str(request.POST.get("tempat_terbit", "")),
                jenis_koleksi=JenisKoleksi.objects.filter(nama_jenis_koleksi=jk).last(),
                sumber_koleksi=SumberKoleksi.objects.filter(nama_sumber_koleksi=sk).last(),
                topik_koleksi=TopikKoleksi.objects.filter(nama_topik_koleksi=tpk).last(),
                bahasa_koleksi=BahasaKoleksi.objects.filter(nama_bahasa_koleksi=bhs).last(),
                status_ketersediaan="1"
            )
            obj.save()
        else:
            tpk = request.POST.get("topik_koleksi")
            bhs = str(request.POST.get("bahasa_koleksi"))
            obj = Koleksi(
                kode_eksamplar=get_kode_eksamplar(jk, sk, thn, no),
                isbn_issn=str(request.POST.get("isbn_issn", "")),
                no_panggil=str(request.POST.get("no_panggil", "")),
                judul=str(request.POST.get("judul_koleksi", "")),
                pengarang=str(request.POST.get("pengarang", "")),
                penerbit=str(request.POST.get("penerbit", "")),
                tahun_terbit=str(request.POST.get("tahun_terbit", "")),
                tempat_terbit=str(request.POST.get("tempat_terbit", "")),
                jenis_koleksi=JenisKoleksi.objects.filter(nama_jenis_koleksi=jk).last(),
                sumber_koleksi=SumberKoleksi.objects.filter(nama_sumber_koleksi=sk).last(),
                bahasa_koleksi=BahasaKoleksi.objects.filter(nama_bahasa_koleksi=bhs).last(),
                topik_koleksi=TopikKoleksi.objects.filter(nama_topik_koleksi=tpk).last(),
                status_ketersediaan="1",
                gambar=request.FILES['file_gambar']
            )
            obj.save()
        return redirect(daftarkoleksi)
    return render(request, 'tambahKoleksi.html', { "kode_koleksi": get_jk, "kode_sumber": get_sk,
                                                   "kode_topik": get_tk, "kode_bahasa": get_bk})


@login_required
def uploadkoleksi(request):
    try:
        if request.method == 'POST' and request.FILES['fileKoleksi']:
            fileKoleksi = request.FILES['fileKoleksi']
            fs = FileSystemStorage()
            filename = fs.save(fileKoleksi.name, fileKoleksi)
            fname = join(dirname(dirname(abspath(__file__))), '', fileKoleksi.name)
            book = xlrd.open_workbook(fname)
            sheet = book.sheet_by_index(0)
            print(sheet.nrows)
            for i in range(1, sheet.nrows):
                print(i)
                jk = str(sheet.row(i)[7].value)
                print(jk)
                shit = JenisKoleksi.objects.filter(kode_koleksi=jk).last()
                print(shit)
                sk = str(sheet.row(i)[8].value)
                print(SumberKoleksi.objects.filter(kode_sumber=sk).last())
                thn = str(sheet.row(i)[11].value)[2:4]
                no = str(sheet.row(i)[12].value)
                tpk = str(sheet.row(i)[9].value)[0:2]
                if (tpk.__contains__('.')):
                    tpk = str(sheet.row(i)[9].value)[0:1]
                print(TopikKoleksi.objects.filter(kode_topik=tpk).last())
                bhs = str(sheet.row(i)[10].value)
                print(BahasaKoleksi.objects.filter(kode_bahasa=bhs).last())
                print(jk, sk, thn, no, tpk, bhs)
                obj = Koleksi(kode_eksamplar=kode_eksamplar(jk, sk, thn, no),
                    isbn_issn=sheet.row(i)[0].value,
                    no_panggil=str(sheet.row(i)[1].value),
                    judul=str(sheet.row(i)[2].value),
                    pengarang=str(sheet.row(i)[3].value),
                    penerbit=str(sheet.row(i)[4].value),
                    tahun_terbit=str(sheet.row(i)[5].value),
                    tempat_terbit=str(sheet.row(i)[6].value),
                    jenis_koleksi=shit,
                    sumber_koleksi=SumberKoleksi.objects.filter(kode_sumber=sk).last(),
                    topik_koleksi=TopikKoleksi.objects.filter(kode_topik=tpk).last(),
                    bahasa_koleksi=BahasaKoleksi.objects.filter(kode_bahasa=bhs).last(),
                    status_ketersediaan="1"
                    )
                obj.save()
                print("saveddd")
            return redirect(daftarkoleksi)
        else:
            return render(request, 'uploadKoleksi.html')
    except:
        messages.error(request, 'failed to upload data, please check your data first.')
        return render(request, 'uploadKoleksi.html')


@login_required
def ubahkoleksi(request):
    if request.method == 'POST':
        kode_eks = str(request.POST.get("kode_eksamplar", ""))
        print(kode_eks)
        get_kode = Koleksi.objects.filter(kode_eksamplar=kode_eks).last()
        print(get_kode)
        filepath = request.FILES.get('file_gambar', False)
        tpk = str(request.POST.get("topik_koleksi", ""))
        bhs = str(request.POST.get("bahasa_koleksi", ""))
        if filepath is True:
            get_kode.isbn_issn = str(request.POST.get("isbn_issn", ""))
            get_kode.no_panggil = str(request.POST.get("no_panggil", ""))
            get_kode.judul = str(request.POST.get("judul_koleksi", ""))
            get_kode.pengarang = str(request.POST.get("pengarang", ""))
            get_kode.penerbit = str(request.POST.get("penerbit", ""))
            get_kode.tahun_terbit = str(request.POST.get("tahun_terbit", ""))
            get_kode.tempat_tebit = str(request.POST.get("tempat_terbit", ""))
            get_kode.topik_koleksi = TopikKoleksi.objects.filter(nama_topik_koleksi=tpk).last()
            get_kode.bahasa_koleksi = BahasaKoleksi.objects.filter(nama_bahasa_koleksi=bhs).last()
            get_kode.gambar = request.FILES['file_gambar']
            get_kode.save()
        else:
            get_kode.isbn_issn = str(request.POST.get("isbn_issn", ""))
            get_kode.no_panggil = str(request.POST.get("no_panggil", ""))
            get_kode.judul = str(request.POST.get("judul_koleksi", ""))
            get_kode.pengarang = str(request.POST.get("pengarang", ""))
            get_kode.penerbit = str(request.POST.get("penerbit", ""))
            get_kode.tahun_terbit = str(request.POST.get("tahun_terbit", ""))
            get_kode.tempat_tebit = str(request.POST.get("tempat_terbit", ""))
            get_kode.topik_koleksi = TopikKoleksi.objects.filter(nama_topik_koleksi=tpk).last()
            get_kode.bahasa_koleksi = BahasaKoleksi.objects.filter(nama_bahasa_koleksi=bhs).last()
            get_kode.save()
        return redirect(daftarkoleksi)
    return redirect(daftarkoleksi)


#Manajemen Transaksi
    #Peminjaman
@login_required
def daftarpeminjaman(request):
    get_pinjam =TransaksiPeminjaman.objects.filter(status_peminjaman=1)
    get_status_denda = StaticVariable.objects.values_list("status", flat=True).get(id=1)
    denda = None
    obj = None
    for i in get_pinjam:
        print(i.kode_pinjam)
        is_denda = Denda.objects.filter(kode_transaksi=i.kode_pinjam).last()
        print(is_denda)
        if is_denda:
            status_denda = Denda.objects.values_list("status_denda", flat=True).get(kode_transaksi=i.kode_pinjam)
            if status_denda == "Aktif":
                denda = True
        else:
            denda = False
        obj = {
            "kode_pinjam": get_pinjam,
            "denda": denda,
            "status": get_status_denda
        }
    if request.method == 'POST':
        if request.POST['form-type'] == u"pinjam_forms":
            if 'change' in request.POST:
                get_kode = str(request.POST.get("kode_pinjam"))
                kode_eks = str(request.POST.get("kode_eksamplar"))
                #set status peminjaman
                Obj = TransaksiPeminjaman.objects.filter(kode_pinjam=get_kode).last()
                Obj.status_peminjaman = '0'
                Obj.tanggal_kembali = datetime.date.today()
                Obj.save()
                #set status koleksi
                koleksi = Koleksi.objects.filter(kode_eksamplar=kode_eks).last()
                koleksi.status_ketersediaan = '1'
                koleksi.save()
                #set notifikasi
                mhs_nimm = TransaksiPeminjaman.objects.values_list("nim", flat=True).get(kode_pinjam=get_kode)
                print(mhs_nimm)
                mhs = Mahasiswa.objects.filter(nim=mhs_nimm).last()
                print(mhs)
                notif = Notifikasi(user=mhs,
                                   message='Beri rating pelayanan Ruang Baca FILKOM',
                                   kode_pinjam=Obj)
                notif.save()
                return redirect(daftarpeminjaman)
            elif 'delete' in request.POST:
                get_transaksi_id = request.POST.get("kode_pinjam", "")
                get_transaksi = TransaksiPeminjaman.objects.filter(kode_pinjam=get_transaksi_id)
                get_transaksi.delete()
    return render(request, 'daftarTransaksiPeminjaman.html', obj)


# @login_required
def tambahpeminjaman(request):
    if request.method == 'POST':
        if request.POST['form-type'] == u"nim_forms":
            get_nim = str(request.POST.get("nim"))
            print(get_nim)
            get_kode = str(request.POST.get("kode_eksamplar"))
            print(get_kode)
            nim = Mahasiswa.objects.filter(status_mahasiswa=1, nim=get_nim)
            kode_eksamplar = Koleksi.objects.filter(kode_eksamplar=get_kode)
            print(nim, kode_eksamplar)
            if nim and kode_eksamplar:
                get_status_koleksi = Koleksi.objects.values_list("status_ketersediaan", flat=True).get(kode_eksamplar=get_kode)
                get_jenis = Koleksi.objects.values_list("jenis_koleksi", flat=True).get(kode_eksamplar=get_kode)
                print(get_jenis)
                if get_status_koleksi is 1:
                    if get_jenis == "B":
                        obj = {
                            "nim": nim,
                            "kode_eksamplar": kode_eksamplar
                        }
                        print("object passed sucessfully")
                        return render(request, 'tambahPeminjaman.html', obj)
                    else:
                        print('Jenis koleksi tidak dapat dipinjam')
                        messages.error(request, 'Jenis koleksi tidak dapat dipinjam')
                else:
                    print('Buku tidak tersedia')
                    messages.error(request, 'Buku tidak tersedia')
            else:
                messages.error(request, 'NIM/Kode Eksamplar yang dimasukkan salah/tidak terdaftar')
        elif request.POST['form-type'] == u"pinjam_forms":
                nim_mhs = str(request.POST.get("nim_mhs"))
                kode_eks = str(request.POST.get("kode_eksamplar"))
                mhs = Mahasiswa.objects.filter(nim=nim_mhs).last()
                koleksi = Koleksi.objects.filter(kode_eksamplar=kode_eks).last()
                print(nim_mhs)
                obj = TransaksiPeminjaman(
                    kode_eksamplar_id=koleksi,
                    tanggal_pinjam=str(request.POST.get("tgl_pinjam")),
                    tanggal_kembali='9999-9-9',
                    status_peminjaman='1',
                    nim_id=mhs
                )
                obj.save()
                tgl_pjm = TransaksiPeminjaman.objects.values_list("tanggal_pinjam", flat=True).last()
                obj.tanggal_kembali = tgl_pjm + timedelta(days=5)
                obj.save()
                koleksi.status_ketersediaan = "0"
                koleksi.save()
                return redirect(daftarpeminjaman)
    return render(request, 'peminjamanNim.html')


    #Pemesanan
@login_required
def daftarpemesanan(request):
    get_pesan = TransaksiPemesanan.objects.filter(status_pemesanan=1)
    obj = {
        "kode_pesan": get_pesan
    }
    if request.method == 'POST':
        if request.POST['form-type'] == u"pesan_forms":
            if 'change' in request.POST:
                get_kode = str(request.POST.get("kode_pesan"))
                cek_kode_pesan = TransaksiPemesanan.objects.filter(kode_pesan=get_kode)
                print(len(cek_kode_pesan))
                kode_eks = str(request.POST.get("kode_eksamplar"))
                cek_kode_eks = TransaksiPemesanan.objects.filter(kode_eksamplar=kode_eks)
                jum = len(cek_kode_eks)
                print("jum={0}".format(jum))
                if jum > 1:
                    print("masuk sini")
                    for i in cek_kode_eks.exclude(kode_pesan=get_kode):
                        print(i)
                        Obj = TransaksiPemesanan.objects.filter(kode_eksamplar=kode_eks).last()
                        Obj.antrian -= 1
                        Obj.save()
                Obj = TransaksiPemesanan.objects.filter(kode_pesan=get_kode).last()
                print(Obj)
                Obj.status_pemesanan = '0'
                Obj.save()
                return redirect(daftarpemesanan)
            elif 'delete' in request.POST:
                get_transaksi_id = request.POST.get("kode_pesan", "")
                get_transaksi = TransaksiPemesanan.objects.filter(kode_pesan=get_transaksi_id)
                get_transaksi.delete()
    return render(request, 'daftarTransaksiPemesanan.html', obj)


#@login_required
def tambahpemesanan(request):
    if request.method == 'POST':
        if request.POST['form-type'] == u"nim_forms":
            get_nim = str(request.POST.get("nim"))
            get_kode = str(request.POST.get("kode_eksamplar"))
            nim = Mahasiswa.objects.filter(nim=get_nim)
            kode_eksamplar = Koleksi.objects.filter(kode_eksamplar=get_kode)
            if nim and kode_eksamplar:
                status_koleksi = Koleksi.objects.values_list("status_ketersediaan", flat=True).get(kode_eksamplar=get_kode)
                if status_koleksi is 0:
                    jenis_koleksi = Koleksi.objects.values_list("jenis_koleksi", flat=True).get(kode_eksamplar=get_kode)
                    if jenis_koleksi == "B":
                        obj = {
                            "nim": nim,
                            "kode_eksamplar": kode_eksamplar
                        }
                        print("object saved sucessfully")
                        return render(request, 'tambahPemesanan.html', obj)
                    else:
                        print("Koleksi yang dapat dipesan adalah koleksi jenis Buku")
                        messages.error(request, 'Koleksi yang dapat dipesan adalah koleksi jenis Buku')
                elif status_koleksi is 1:
                    print('Buku yang dipesan sudah tersedia, silahkan lakukan peminjaman')
                    messages.error(request, 'Buku yang dipesan sudah tersedia, silahkan lakukan peminjaman')
                    return render(request, 'peminjamanNim.html')
            else:
                messages.error(request, 'NIM/Kode Eksamplar yang dimasukkan salah/tidak terdaftar')
        elif request.POST['form-type'] == u"ps_forms":
            nim_mhs = str(request.POST.get("nim_mhs"))
            kode_eks = str(request.POST.get("kode_eksamplar"))
            mhs = Mahasiswa.objects.filter(nim=nim_mhs).last()
            print(mhs)
            koleksi = Koleksi.objects.filter(kode_eksamplar=kode_eks).last()
            print(koleksi)
            cek_antrian = TransaksiPemesanan.objects.filter(kode_eksamplar=koleksi, status_pemesanan=1)
            print(cek_antrian)
            if not cek_antrian:
                obj = TransaksiPemesanan(
                    kode_eksamplar_id=kode_eks,
                    tanggal_pesan=str(request.POST.get("tgl_pesan")),
                    status_pemesanan='1',
                    nim_id=nim_mhs,
                    antrian=1
                )
                obj.save()
            else:
                get_antrian = TransaksiPemesanan.objects.values_list('antrian', flat=True).get(kode_eksamplar=kode_eks)
                print(get_antrian)
                antrian = get_antrian + 1
                print(antrian)
                obj = TransaksiPemesanan(
                    kode_eksamplar_id=kode_eks,
                    tanggal_pesan=str(request.POST.get("tgl_pesan")),
                    status_pemesanan='1',
                    nim_id=nim_mhs,
                    antrian=antrian
                )
                obj.save()
            return redirect(daftarpemesanan)
    return render(request, 'pemesananNim.html')


# Pengaturan
@login_required
def cetakbarkode(request):
    get_koleksi = Koleksi.objects.all()
    obj = {
        "kode_eksamplar": get_koleksi
    }
    if request.method == "POST":
        a = request.POST.getlist('checklist')
        print(a)
        for i in a:
            print(i)
            writer = ImageWriter()
            ean = barcode.Code39(i, writer, add_checksum= False)
            ean.save('Code39{0}'.format(i))
        obj = {
            'img': a
        }
        print(obj)
        return render(request, 'barkode.html', obj)
    return render(request, 'cetakBarkodeKoleksi.html', obj)


# Anggota
@login_required
def daftaranggota(request):
    try:
        mhs = Mahasiswa.objects.filter(status_mahasiswa=1)
        return render(request, 'daftarAnggota.html', {'nim': mhs})
    except urllib.error.HTTPError:
        print('fail')
    except urllib.error.URLError:
        print('url error')
    return render(request, 'daftarAnggota.html')


# Skripsi
@login_required
def daftarskripsi(request):
    try:
        urllib.request.urlopen('http://127.0.0.1:9000/skripsi')
        response = requests.get('http://127.0.0.1:9000/skripsi')
        skripsi = response.json()
        return render(request, 'daftarSkripsi.html', {'id': skripsi})
    except urllib.error.HTTPError:
        print('http error')
    except urllib.error.URLError:
        print('url error')
    return render(request, 'daftarSkripsi.html')


def abstrakskripsi(request, id):
    id_skripsi = id
    response = requests.get('http://127.0.0.1:9000/skripsi/{0}'.format(id_skripsi))
    skripsi = response.json()
    return render_to_response('abstrakSkripsi.html', skripsi)


# Akun Pengguna
@login_required
def daftarakunpengguna(request):
    get_admin = User.objects.filter(is_superuser=True)
    get_staff = User.objects.filter(groups=2)
    obj = {
        "id": get_admin,
        "staff": get_staff
    }
    if request.method == 'POST':
        if request.POST['form-type'] == u"admin_forms":
            if 'change' in request.POST:
                get_admin_id = request.POST.get("username", "")
                print(get_admin_id)
                get_admin = User.objects.filter(username=get_admin_id, is_superuser=True)
                print(get_admin)
                obj = {
                    "id": get_admin
                }
                return render(request, 'ubahAkunPengguna.html', obj)
            elif 'delete' in request.POST:
                get_admin_id = request.POST.get("username", "")
                print(get_admin_id)
                get_admin = User.objects.filter(username=get_admin_id)
                get_admin.delete()
        elif request.POST['form-type'] == u"staff_forms":
            if 'change' in request.POST:
                get_staff_id = request.POST.get("username", "")
                print(get_staff_id)
                get_staff = User.objects.filter(username=get_staff_id, is_superuser=False)
                obj = {
                    "id": get_staff
                }
                return render(request, 'ubahAkunPengguna.html', obj)
            elif 'delete' in request.POST:
                get_staff_id = request.POST.get("username", "")
                print(get_staff_id)
                get_jk = User.objects.filter(username=get_staff_id)
                get_jk.delete()
    return render(request, 'daftarAkunPengguna.html', obj)


@login_required
def tambahakunpengguna(request):
    get_group = Group.objects.all()
    obj = {
        "id": get_group
    }
    if request.method == "POST":
        is_admin = str(request.POST.get("tipe_pengguna"))
        if is_admin == "staff":
            a = User(
                first_name=str(request.POST.get("nama_pengguna", "")),
                username=str(request.POST.get("username", "")),
                password=str(request.POST.get("password_pengguna", "")),
                is_superuser=False,
                is_staff=True,
                is_active=True
            )
            x = a.save()
            a_id = User.objects.all().last()
            staff_group = Group.objects.get(name="staff")
            staff_group.user_set.add(a_id)
        elif is_admin == "admin":
            a = User(
                first_name=str(request.POST.get("nama_pengguna", "")),
                username=str(request.POST.get("username", "")),
                password=str(request.POST.get("password_pengguna", "")),
                is_superuser=True,
                is_staff=True,
                is_active=True,
            )
            x = a.save()
            a_id = User.objects.all().last()
            admin_group = Group.objects.get(name="admin")
            admin_group.user_set.add(a_id)
        if x is None:
            return redirect(daftarakunpengguna)
        else:
            messages.error(request, 'Failed to Save Object!')
            return render(request, 'tambahAkunPengguna.html')
    return render(request, 'tambahAkunPengguna.html', obj)


@login_required
def ubahakunpengguna(request):
    get_user = User.objects.all()
    print(get_user)
    if request.method == "POST":
        is_admin = str(request.POST.get("tipe_pengguna", ""))
        print(is_admin)
        if is_admin == "admin":
            superuser = True
        else:
            superuser = False
        print(superuser)
        obj = User.objects.all().last()
        obj.first_name = str(request.POST.get("nama_pengguna", ""))
        obj.username = str(request.POST.get("username", ""))
        obj.passwrod = str(request.POST.get("password_pengguna", ""))
        obj.is_superuser = superuser
        obj.save()
        return redirect(daftarakunpengguna)
    return render(request, 'ubahAkunPengguna.html', {"id": get_user})


# daftar jenis,topik,sumber,bahasa
@login_required
def daftarjeniskoleksi(request):
    get_jk = JenisKoleksi.objects.all()
    get_sk = SumberKoleksi.objects.all()
    get_tk = TopikKoleksi.objects.all()
    get_bk = BahasaKoleksi.objects.all()
    if request.method == 'POST':
        if request.POST['form-type'] == u"jk_forms":
            if 'change' in request.POST:
                get_jk_kode = request.POST.get("kode_koleksi", "")
                print(get_jk_kode)
                get_jk = JenisKoleksi.objects.filter(kode_koleksi=get_jk_kode)
                jk = {
                    "kode_koleksi": get_jk
                }
                return render(request, 'ubahJenisKoleksi.html', jk)
            elif 'delete' in request.POST:
                get_jk_kode = request.POST.get("kode_koleksi", "")
                print(get_jk_kode)
                get_jk = JenisKoleksi.objects.filter(kode_koleksi=get_jk_kode)
                get_jk.delete()
        elif request.POST['form-type'] == u"sk_forms":
            if 'change' in request.POST:
                get_sk_kode = request.POST.get("kode_sumber", "")
                print(get_sk_kode)
                get_sk = SumberKoleksi.objects.filter(kode_sumber=get_sk_kode)
                sk = {
                    "kode_sumber": get_sk
                }
                return render(request, 'ubahSumberKoleksi.html', sk)
            elif 'delete' in request.POST:
                get_sk_kode = request.POST.get("kode_sumber", "")
                print(get_sk_kode)
                get_sk = SumberKoleksi.objects.filter(kode_sumber=get_sk_kode)
                get_sk.delete()
        elif request.POST['form-type'] == u"bk_forms":
            if 'change' in request.POST:
                get_bk_kode = request.POST.get("kode_bahasa", "")
                print(get_bk_kode)
                get_bk = BahasaKoleksi.objects.filter(kode_bahasa=get_bk_kode)
                bk = {
                    "kode_bahasa": get_bk
                }
                return render(request, 'ubahBahasaKoleksi.html', bk)
            elif 'delete' in request.POST:
                get_bk_kode = request.POST.get("kode_bahasa", "")
                print(get_bk_kode)
                get_bk = BahasaKoleksi.objects.filter(kode_bahasa=get_bk_kode)
                get_bk.delete()
        elif request.POST['form-type'] == u"tk_forms":
            if 'change' in request.POST:
                get_tk_kode = request.POST.get("kode_topik", "")
                print(get_tk_kode)
                get_tk = TopikKoleksi.objects.filter(kode_topik=get_tk_kode)
                tk = {
                    "kode_topik": get_tk
                }
                return render(request, 'ubahTopikKoleksi.html', tk)
            elif 'delete' in request.POST:
                get_tk_kode = request.POST.get("kode_topik", "")
                print(get_tk_kode)
                get_tk = BahasaKoleksi.objects.filter(kode_bahasa=get_tk_kode)
                get_tk.delete()
    return render(request, 'daftarJenisKoleksi.html', {"kode_koleksi": get_jk, "kode_sumber": get_sk,
                                                  "kode_topik": get_tk, "kode_bahasa": get_bk})


#Jenis Koleksi
@login_required
def ubahjeniskoleksi(request):
    get_jk = JenisKoleksi.objects.all()
    if request.method == "POST":
        obj = JenisKoleksi(
            kode_koleksi= str(request.POST.get("kode_jenis_koleksi", "")),
            nama_jenis_koleksi= str(request.POST.get("nama_jenis_koleksi", ""))
        )
        a = obj.save()
        if a is None:
            return redirect(daftarjeniskoleksi)
        else:
            messages.error(request, 'Failed to Save Object!')
            return render(request, 'ubahJenisKoleksi.html')
    return render(request, 'ubahJenisKoleksi.html', { "kode_koleksi": get_jk})


@login_required
def tambahjeniskoleksi(request):
    if request.method == "POST":
        obj = JenisKoleksi(
            kode_koleksi= str(request.POST.get("kode_jenis_koleksi", "")),
            nama_jenis_koleksi= str(request.POST.get("nama_jenis_koleksi", ""))
        )
        a = obj.save()
        if a is None:
            messages.success(request, 'Object Saved!')
            obj = {
                "x": True
            }
            return render(request, 'tambahJenisKoleksi.html', obj)
        else:
            messages.error(request, 'Failed to Save Object!')
            return render(request, 'tambahJenisKoleksi.html')
    return render(request, 'tambahJenisKoleksi.html')


# Topik Koleksi
@login_required
def ubahtopikkoleksi(request):
    get_tk = TopikKoleksi.objects.all()
    if request.method == "POST":
        obj = TopikKoleksi(
            kode_topik=str(request.POST.get("kode_topik_koleksi", "")),
            nama_topik_koleksi=str(request.POST.get("nama_topik_koleksi", ""))
        )
        a = obj.save()
        if a is None:
            return redirect(daftarjeniskoleksi)
        else:
            messages.error(request, 'Failed to Save Object!')
            return render(request, 'ubahTopikKoleksi.html')
    return render(request, 'ubahTopikKoleksi.html', {"kode_topik": get_tk})


@login_required
def tambahtopikkoleksi(request):
    if request.method == "POST":
        obj = TopikKoleksi(
            kode_topik=str(request.POST.get("kode_topik_koleksi", "")),
            nama_topik_koleksi= str(request.POST.get("nama_topik_koleksi", ""))
        )
        a = obj.save()
        if a is None:
            messages.success(request, 'Object Saved!')
            obj = {
                "x": True
            }
            return render(request, 'tambahTopikKoleksi.html', obj)
        else:
            messages.error(request, 'Failed to Save Object!')
            return render(request, 'tambahTopikKoleksi.html')
    return render(request, 'tambahTopikKoleksi.html')


# Sumber Koleksi
@login_required
def ubahsumberkoleksi(request):
    get_sk = SumberKoleksi.objects.all()
    if request.method == "POST":
        obj = SumberKoleksi(
            kode_sumber=str(request.POST.get("kode_sumber_koleksi", "")),
            nama_sumber_koleksi=str(request.POST.get("nama_sumber_koleksi", ""))
        )
        a = obj.save()
        if a is None:
            return redirect(daftarjeniskoleksi)
        else:
            messages.error(request, 'Failed to Save Object!')
            return render(request, 'ubahJenisKoleksi.html')
    return render(request, 'ubahSumberKoleksi.html', {"kode_koleksi": get_sk})


@login_required
def tambahsumberkoleksi(request):
    if request.method == "POST":
        obj = SumberKoleksi(
            kode_sumber= str(request.POST.get("kode_sumber_koleksi", "")),
            nama_sumber_koleksi= str(request.POST.get("nama_sumber_koleksi", ""))
        )
        a = obj.save()
        if a is None:
            messages.success(request, 'Object Saved!')
            obj = {
                "x": True
            }
            return render(request, 'tambahSumberKoleksi.html', obj)
        else:
            messages.error(request, 'Failed to Save Object!')
            return render(request, 'tambahSumberKoleksi.html')
    return render(request, 'tambahSumberKoleksi.html')


# Bahasa Koleksi
@login_required
def ubahbahasakoleksi(request):
    get_bk = BahasaKoleksi.objects.all()
    if request.method == "POST":
        obj = BahasaKoleksi(
            kode_bahasa=str(request.POST.get("kode_bahasa_koleksi", "")),
            nama_bahasa_koleksi=str(request.POST.get("nama_bahasa_koleksi", ""))
        )
        a = obj.save()
        if a is None:
            return redirect(daftarjeniskoleksi)
        else:
            messages.error(request, 'Failed to Save Object!')
            return render(request, 'ubahBahasaKoleksi.html')
    return render(request, 'ubahBahasaKoleksi.html', {"kode_bahasa": get_bk})


@login_required
def tambahbahasakoleksi(request):
    if request.method == "POST":
        obj = BahasaKoleksi(
            kode_bahasa=str(request.POST.get("kode_bahasa_koleksi", "")),
            nama_bahasa_koleksi= str(request.POST.get("nama_bahasa_koleksi", ""))
        )
        a = obj.save()
        if a is None:
            messages.success(request, 'Object Saved!')
            obj = {
                "x": True
            }
            return render(request, 'tambahBahasaKoleksi.html', obj)
        else:
            messages.eror(request, 'Failed to Save Object!')
            return render(request, 'tambahBahasaKoleksi.html')
    return render(request, 'tambahBahasaKoleksi.html')


#riwayatPeminjaman
@login_required
def riwayatpeminjaman(request):
    get_transaksi = TransaksiPeminjaman.objects.filter(status_peminjaman=0)
    obj = {
        "kode_pinjam": get_transaksi
    }
    return render(request, 'riwayatPeminjaman.html', obj)


#riwayatPemesanan
@login_required
def riwayatpemesanan(request):
    get_transaksi = TransaksiPemesanan.objects.filter(status_pemesanan=0)
    obj = {
        "kode_pesan": get_transaksi
    }
    return render(request, 'riwayatPemesanan.html', obj)


def laporan(request):
    anggota = Mahasiswa.objects.values('Angkatan').annotate(c=Count('Angkatan'))
    angkatan_total = Mahasiswa.objects.all().count()
    jenis_koleksi = Koleksi.objects.values('jenis_koleksi').annotate(c=Count('kode_eksamplar'), a=Count('judul'))
    jenis_topik = Koleksi.objects.values('topik_koleksi').annotate(c=Count('kode_eksamplar'), a=Count('judul'))
    print(jenis_topik)
    jum_koleksi= Koleksi.objects.all().count()
    jum_peminjaman = TransaksiPeminjaman.objects.all().count()
    jum_pemesanan = TransaksiPemesanan.objects.all().count()
    total_transaksi = jum_peminjaman + jum_pemesanan
    transaksi_judul = TransaksiPeminjaman.objects.values('kode_eksamplar').annotate(c=Count('kode_eksamplar'))
    transaksi_topik = TransaksiPeminjaman.objects.values('kode_eksamplar__topik_koleksi').annotate(c=Count('kode_eksamplar'))
    print(transaksi_topik)
    a = {
        "anggota": anggota,
        "angkatan_total": angkatan_total,
        "jenis_koleksi": jenis_koleksi,
        "jenis_topik": jenis_topik,
        "jum_koleksi": jum_koleksi,
        "jum_peminjaman": jum_peminjaman,
        "jum_pemesanan": jum_pemesanan,
        "total_transaksi": total_transaksi,
        "transaksi_judul": transaksi_judul,
        "transaksi_topik": transaksi_topik
    }
    return render(request, 'laporan.html', a)


@login_required
def cetaklaporan(request):
    months = TransaksiPeminjaman.objects.annotate(month=TruncMonth('tanggal_pinjam')).values('month')\
        .annotate(c=Count('kode_pinjam'))
    years = TransaksiPeminjaman.objects.annotate(year=TruncYear('tanggal_pinjam')).values('year')\
        .annotate(c=Count('kode_pinjam'))
    dataSource={}
    dataSource['chart'] = {
        "caption": "Rekap Feedback Anggota Terhadap Pelayanan Ruang Baca FILKOM UB",
        "plottooltext": "<b>$percentValue</b> anggota memberikan rating $label",
        "showlegend": "1",
        "showpercentvalues": "1",
        "legendposition": "bottom",
        "usedataplotcolorforlabels": "1",
        "theme": "fusion"
    }
    dataSource['data'] = []
    a = Feedback.objects.all()
    b = list(Feedback.objects.values('rating').annotate(c=Count('rating')))
    print(b)
    for i in b:
        print(i['rating'])
        print(i['c'])
        data = {}
        data['label'] = str(i['rating'])
        data['value'] = i['c']
        dataSource['data'].append(data)

    feedbackChart = FusionCharts("pie2d", "ex1", "400", "300", "chart-1", "json", dataSource)
    feedback = Feedback.objects.all()
    object = {
        "months": months,
        "years": years,
        "chart": feedbackChart.render(),
        "feedback": feedback
    }
    if request.method == 'POST':
        start_date = str(request.POST.get("start_date"))
        end_date = str(request.POST.get("end_date"))
        transaksi_judul = TransaksiPeminjaman.objects.values('kode_eksamplar__judul')\
            .annotate(c=Count('kode_eksamplar')).filter(tanggal_pinjam__range=[start_date, end_date])
        transaksi_topik = TransaksiPeminjaman.objects.values('kode_eksamplar__topik_koleksi__nama_topik_koleksi')\
            .annotate(c=Count('kode_eksamplar')).filter(tanggal_pinjam__range=[start_date, end_date])
        if transaksi_judul and transaksi_topik:
            anggota = Mahasiswa.objects.values('Angkatan').annotate(c=Count('Angkatan'))
            angkatan_total = Mahasiswa.objects.all().count()
            jenis_koleksi = Koleksi.objects.values('jenis_koleksi__nama_jenis_koleksi').annotate(c=Count('kode_eksamplar'),
                                                                             a=Count('judul'))
            tos = Koleksi.objects.values('judul').annotate(a=Count('judul'))
            print(tos.all())
            count_tos = 0
            for i in tos:
                count_tos += i['a']
            print(count_tos)
            test = Koleksi.objects.values('judul').order_by('topik_koleksi__nama_topik_koleksi').annotate(a=Count('judul'))
            print(test)
            jenis_topik = Koleksi.objects.values('topik_koleksi__nama_topik_koleksi').annotate(c=Count('kode_eksamplar'), a=Count('judul'))
            jum_koleksi = Koleksi.objects.all().count()
            jum_topik = 0
            for i in jenis_topik:
                jum_topik += i['a']
            jum_peminjaman = transaksi_judul.count()
            jum_pemesanan = TransaksiPemesanan.objects.all().count()
            total_transaksi = jum_peminjaman + jum_pemesanan
            a = {
                "anggota": anggota,
                "angkatan_total": angkatan_total,
                "jenis_koleksi": jenis_koleksi,
                "jenis_topik": jenis_topik,
                "jum_koleksi": jum_koleksi,
                "jum_topik": jum_topik,
                "jum_peminjaman": jum_peminjaman,
                "jum_pemesanan": jum_pemesanan,
                "total_transaksi": total_transaksi,
                "transaksi_judul": transaksi_judul,
                "transaksi_topik": transaksi_topik
            }
            return render(request, 'laporan.html', a)
        else:
            messages.error(request, 'No record found!')
    return render(request, 'laporanPage.html', object)


from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
# Denda
def daftardenda(request):
    denda = Denda.objects.all()
    status = StaticVariable.objects.values_list("status", flat=True).get(id=1)
    obj = {
        "denda":denda,
        "status": status
    }
    if request.is_ajax():
        import json
        data = json.loads(request.POST.get('data'))
        if data == "False":
            status = StaticVariable.objects.filter(id=1).last()
            status.status = True
            status.save()
        elif data == "True":
            status = StaticVariable.objects.filter(id=1).last()
            status.status = False
            status.save()
    return render(request, 'daftarDenda.html', obj)


def get_angkatan(nim):
    print(nim)
    if nim == "215":
        return 2021
    elif nim == "205":
        return 2020
    elif nim == "195":
        return 2019
    elif nim == "185":
        return 2018
    elif nim == "175":
        return 2017
    elif nim == "165":
        return 2016
    elif nim == "155":
        return 2015
    elif nim == "145":
        return 2014
    elif nim == "135":
        return 2013
    elif nim == "125":
        return 2012
    elif nim == "115":
        return 2011