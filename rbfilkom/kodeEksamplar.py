from rbfilkom.models import *


def get_kode_eksamplar(jk,sk,thn,no):
    get_jk_kode = JenisKoleksi.objects.values_list("kode_koleksi", flat=True).get(nama_jenis_koleksi=jk)
    get_sk_kode = SumberKoleksi.objects.values_list("kode_sumber", flat=True).get(nama_sumber_koleksi=sk)
    kode_eksamplar = get_jk_kode + get_sk_kode + '-' + thn + '-' + no
    print(kode_eksamplar)
    return kode_eksamplar


def kode_eksamplar(jk,sk,thn,no):
    kode_eksamplar = jk + sk + '-' + thn + '-' + no
    print(kode_eksamplar)
    return kode_eksamplar