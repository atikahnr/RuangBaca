from django.test import TestCase, LiveServerTestCase
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.common.keys import Keys


class TambahTransaksiPeminjamanTest(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        super(TambahTransaksiPeminjamanTest, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(TambahTransaksiPeminjamanTest, self).tearDown()

    def test_tambahpeminjaman(self):
        selenium = self.selenium
        selenium.get('http://127.0.0.1:8000/rbfilkom/TambahPeminjaman/')
        nim = selenium.find_element_by_id('nimm')
        kode_eksamplar = selenium.find_element_by_id('kode')
        #nim_mhs = selenium.find_element_by_name('nim_mhs')
        #kode_eks = selenium.find_element_by_name('kode_eksamplar')
        #tanggal_pinjam = selenium.find_element_by_name('tgl_pinjam')

        submit = selenium.find_element_by_name('submit_btn')

        nim.send_keys('155150200111044')
        kode_eksamplar.send_keys('B1-17-0333')
        #nim_mhs.send_keys('155150200111044')
        #kode_eks.send_keys('B1-17-0333')
        #tanggal_pinjam.send_keys('2019-2-20')

        submit.send_keys(Keys.RETURN)

        assert 'A' in selenium.page_source

    def test_denda(self):
        selenium = self.selenium
        selenium.get('http://127.0.0.1:8000/rbfilkom/DaftarDenda/')
        status = selenium.find_element_by_id('set_denda')

        status.send_keys('True')
        selenium.execute_script()
        assert 'A' in selenium.page_source


class TambahTransaksiPemesananTest(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        super(TambahTransaksiPemesananTest, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(TambahTransaksiPemesananTest, self).tearDown()

    def test_tambahpemesanan(self):
        selenium = self.selenium
        selenium.get('http://127.0.0.1:8000/rbfilkom/TambahPemesanan/')
        nim = selenium.find_element_by_id('nim')
        kode_eksamplar = selenium.find_element_by_id('kode_eksamplar')
        # nim_mhs = selenium.find_element_by_name('nim_mhs')
        # kode_eks = selenium.find_element_by_name('kode_eksamplar')
        # tanggal_pinjam = selenium.find_element_by_name('tgl_pinjam')

        submit = selenium.find_element_by_name('submit_btn')

        nim.send_keys('155150200111044')
        kode_eksamplar.send_keys('B1-17-0333')

        submit.send_keys(Keys.RETURN)

        assert 'A' in selenium.page_source


class PengujianIntegrasi(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        super(PengujianIntegrasi, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(PengujianIntegrasi, self).tearDown()

    def pengujianIntegrasi1(self):
        selenium = self.selenium
        selenium.get('http://127.0.0.1:8000/rbfilkom/TambahKoleksi/')
        jk = selenium.find_element_by_id('jenis_kol')
        sk = selenium.find_element_by_id('sumber_kol')
        thn = selenium.find_element_by_id('tahun_inv')
        no = selenium.find_element_by_id('no_inv')
        isbn = selenium.find_element_by_id('isbn_issn')
        no_panggil = selenium.find_element_by_id('no_panggil')
        judul = selenium.find_element_by_id('judul_koleksi')
        pengarang = selenium.find_element_by_id('pengarang')
        penerbit = selenium.find_element_by_id('penerbit')
        tahun_terbit = selenium.find_element_by_id('tahun_terbit')
        tempat_terbit = selenium.find_element_by_id('tempat_terbit')
        topik_koleksi = selenium.find_element_by_id('topik_koleksi')
        bahasa_koleksi = selenium.find_element_by_id('bahasa_koleksi')

        submit = selenium.find_element_by_name('submit_btn')

        jk.send_keys('buku')
        sk.send_keys('')
        thn.send_keys('2018')
        no.send_keys('0891')
        isbn.send_keys('1294750302832')
        no_panggil.send_keys('12456')
        judul.send_keys('Buku Test')
        pengarang.send_keys('birald')
        penerbit.send_keys('birald.cv')
        tahun_terbit('2018')
        tempat_terbit.send_keys('Malang')
        topik_koleksi.send_keys('algortima')
        bahasa_koleksi.send_keys('Bahasa Indonesia')

        submit.send_keys(Keys.RETURN)

        assert 'A' in selenium.page_source