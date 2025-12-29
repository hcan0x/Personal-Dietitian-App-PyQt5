import sys
import pymongo
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from ui_dosyasi import Ui_MainWindow # tasarım dosyamız

class DiyetisyenUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Veritabanı Bağlantısı
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["Diyetisyen_kayit"]
        self.kullanicilar_koleksiyonu = self.db["Kullanicilar"]
        
        self.aktif_kullanici = None # Giriş yapan kullanıcıyı burada tutacağız

        # Uygulama açılınca Giriş Ekranı 
        self.ui.stackedWidget.setCurrentIndex(0)


        # 1. GİRİŞ SAYFASI (Page 0)
        # Giriş Yap vutonu
        self.ui.btn_giris_yap.clicked.connect(self.kullanici_giris)
        
        # Kayıt Ol butonu  Kayıt sayfasına yönlendirir
        self.ui.btn_kayit_ol_gecis.clicked.connect(self.sayfa_kayit_ac)


        # 2. KAYIT SAYFASI (Page 1)
        # Kaydet butonu Veritabanına yazar
        self.ui.btn_kaydet_devam.clicked.connect(self.kullanici_kayit)
        
        # Geri Dön butonu  Giriş sayfasına döner
        self.ui.btn_geri_don_giris.clicked.connect(self.sayfa_giris_ac)


        # 3. HEDEF SEÇİM SAYFASI (Page 2)
        # Hedef butonları Hedefi veritabanına yazar ve Ana Ekrana atar
        self.ui.btn_kilo_al.clicked.connect(self.hedef_secimi)
        self.ui.btn_kilo_ver.clicked.connect(self.hedef_secimi)
        self.ui.btn_form_koru.clicked.connect(self.hedef_secimi)

        # Geri Dön butonu  Giriş sayfasına döner
        self.ui.btn_geri_don_hedef.clicked.connect(self.sayfa_giris_ac)

        #GÜNLÜK VERİLER
        self.gunluk_kalori = 0
        self.gunluk_protein = 0
        self.gunluk_karbon = 0
        self.gunluk_yag = 0
        
        self.hedef_kalori = 2000 # rastgele bir sayı verdim
        
        # Dashboard Butonları devreye sokuyoz
        self.ui.btn_yemek_ekle.clicked.connect(self.yemek_ekle)
        self.ui.btn_protein_ekle.clicked.connect(self.protein_ekle)
        self.ui.btn_karbon_ekle.clicked.connect(self.karbon_ekle)
        self.ui.btn_yag_ekle.clicked.connect(self.yag_ekle)
        self.ui.btn_sinav_ekle.clicked.connect(self.spor_ekle)
        self.ui.btn_mekik_ekle.clicked.connect(self.spor_ekle)
        self.ui.btn_barfiks_ekle.clicked.connect(self.spor_ekle)
        self.ui.btn_kosu_ekle.clicked.connect(self.spor_ekle)

        #tebrik mesajı:
        self.tebrik_edildi = False
        

    def sayfa_kayit_ac(self):#kayıt sayafasını açar
        
        self.ui.stackedWidget.setCurrentIndex(1)

    def sayfa_giris_ac(self):#giriş sayfasını açar
        
        self.ui.stackedWidget.setCurrentIndex(0)
    
    def sayfa_hedef_ac(self):#hedef sayfasını açar
       
        self.ui.stackedWidget.setCurrentIndex(2)

    def kullanici_kayit(self):
        
        #kayıt ekranındaki bilgileri veri tabanına aktarma
        ad_soyad = self.ui.line_adsoyad.text()
        kullanici_adi = self.ui.line_kayit_kullanici.text()
        sifre = self.ui.line_kayit_sifre.text()
        yas = self.ui.spin_yas.value()
        kilo = self.ui.spin_kilo.value()

        # 2. Boş alan kontrolü 
        if ad_soyad == "" or kullanici_adi == "" or sifre == "":
            QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurunuz.")
            return

        #  Veriyi paketle (Dict)
        yeni_kullanici = {
            "ad_soyad": ad_soyad,
            "kullanici_adi": kullanici_adi,
            "sifre": sifre,
            "yas": yas,
            "kilo": kilo,
            "hedef": None  # Hedefi sonra seçcek
        }

        # Veritabanına kaydet
        self.kullanicilar_koleksiyonu.insert_one(yeni_kullanici)
        
        # Kullanıcıya haber ver ve Giriş sayfasına yönlendir
        QMessageBox.information(self, "Başarılı", "Kayıt Başarılı! Giriş yapabilirsiniz.")
        self.sayfa_giris_ac()


    def kullanici_giris(self):
        girilen_kadi = self.ui.line_kullanici.text()
        girilen_sifre = self.ui.line_sifre.text()
        
        
        #boşluk kalmasın diye kontrol.
        if girilen_kadi == "" or girilen_sifre == "":
            QMessageBox.warning(self, "Eksik Bilgi!", "Lütfn kullanıcı adı ve şifrenizi doldurunuz.")
            return
         

        kullanici = self.kullanicilar_koleksiyonu.find_one({
              "kullanici_adi": girilen_kadi,
              "sifre": girilen_sifre
         })
        


         #sonuç kontrol
        if kullanici:
            QMessageBox.information(self, "Başarılı", "Giriş başarılı!! Hoş geldiniz.")

            self.aktif_kullanici = kullanici
            self.dashboard_hazirla() # giriş başarılı olduğunda grilen bilgilere göre dashboardı hazırlıyoruz
            self.ui.stackedWidget.setCurrentIndex(2) # 2.sayfaya yönlendiriyoruz
        else:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre yanlış!")

    def hedef_secimi(self):
        secilen_buton = self.sender()
        hedef = ""

        if secilen_buton == self.ui.btn_kilo_al:
            hedef = "kilo al"
        elif secilen_buton == self.ui.btn_kilo_ver:
            hedef = "kilo ver"
        elif secilen_buton == self.ui.btn_form_koru:
             hedef = "formu koru"

        #veritabanında kullanıcınıyı bulup hedef bilgisini güncelleme
        if hasattr(self, "aktif_kullanici") and self.aktif_kullanici:
            self.kullanicilar_koleksiyonu.update_one(
                {"_id": self.aktif_kullanici["_id"]}, 
                {"$set": {"hedef": hedef}}
            )

            QMessageBox.information(self, "Hedef Belirlendi", f"Heefiniz '{hedef}' olarak ayarlandı.")
            self.ui.stackedWidget.setCurrentIndex(3)

            # 2. HAFIZAYI GÜNCELLE
            self.aktif_kullanici["hedef"] = hedef 

            # 3. HESAP MAKİNESİNİ ÇALIŞTIR
            self.dashboard_hazirla()

            # 4. Bilgi Ver ve Sayfayı Değiştir
            QMessageBox.information(self, "Hedef Belirlendi", f"Hedefiniz '{hedef}' olarak ayarlandı.")
            self.ui.stackedWidget.setCurrentIndex(3) # Sayfa değişimi en sonda
        else:
            QMessageBox.warning(self, "Hata", "oturum açmış kullanıcı bulunamadu!")


    def dashboard_hazirla(self):
        #kullanıcının verilerine göre hesap makinesi yapcaz
        if not self.aktif_kullanici:
            return

        kilo = self.aktif_kullanici.get("kilo", 70)
        yas = self.aktif_kullanici.get("yas", 25)
        hedef = self.aktif_kullanici.get("hedef", "form koru")

        #KALORİ HESAP FORMÜLÜ (KENDİM BELİRLEDİĞİM):
        # kilo* 24 saat * aktivite(1.2) = metabolizma # 75 * 24 * 1.2 = 2160 ihtiyacım olan kalori
        bazal_metabolizma = kilo * 24 *1.2

        if hedef == "kilo ver":
            self.hedef_kalori = bazal_metabolizma - 500

        elif hedef == "kilo al":
            self.hedef_kalori = bazal_metabolizma + 500

        else:
            self.hedef_kalori = bazal_metabolizma   

        #MAKRO HESABI :
        # ortalama spor diyet oranı : %40 karbon, %30 protein, %30 yağ
        # 1gr protein = 4 kalori
        # 1gr karb = 4 kalori
        # 1gr yağ = 9 kalori

        hedef_protein_gram = (self.hedef_kalori * 0.30) / 4
        hedef_karbon_gram = (self.hedef_kalori * 0.40) / 4
        hedef_yag_gram = (self.hedef_kalori * 0.30) / 9

        #görevler:
        h_kosu, h_mekik, h_sinav, h_barfiks = 5, 100, 100, 50
        
        if hedef == "kilo almak":
            h_kosu, h_mekik, h_sinav, h_barfiks = 2, 50, 50, 50
            
        elif hedef == "kilo vermek":
            h_kosu, h_mekik, h_sinav, h_barfiks = 10, 200, 200, 100

        #barları 0 la (spor)

        self.ui.bar_kosu.setMaximum(h_kosu)
        self.ui.bar_kosu.setValue(0) # O 24% yazısını siler, 0 yapar.
        
        self.ui.bar_mekik.setMaximum(h_mekik)
        self.ui.bar_mekik.setValue(0)
        
        self.ui.bar_sinav.setMaximum(h_sinav)
        self.ui.bar_sinav.setValue(0)
        
        self.ui.bar_barfiks.setMaximum(h_barfiks)
        self.ui.bar_barfiks.setValue(0)


        #vücut kitle endeksi hesaplama

        boy = 1.75
        bmi = kilo / (boy* boy)

        if bmi < 18.5: durum = "Zayıf"
        elif bmi < 25: durum = "Normal"
        elif bmi < 30: durum = "Fazla Kilolu"
        else: durum = "Obez"


        mesaj = (f"GÖREV: Koşu:{h_kosu}km Mekik:{h_mekik} Şınav:{h_sinav} Barfiks:{h_barfiks}\n"
                 f"HEDEF: {hedef_protein_gram:.0f}g Prot • {hedef_karbon_gram:.0f}g Karb • {hedef_yag_gram:.0f}g Yağ")
        
        


        #PROGRESS BARLARININ MAKS AYARI
        self.ui.bar_kalori.setMaximum(int(self.hedef_kalori))
        self.ui.bar_protein.setMaximum(int(hedef_protein_gram))
        self.ui.bar_karbon.setMaximum(int(hedef_karbon_gram))
        self.ui.bar_yag.setMaximum(int(hedef_yag_gram))


        #barları sıfırlıyoruz
        self.ui.bar_kalori.setValue(0)
        self.ui.bar_protein.setValue(0)
        self.ui.bar_karbon.setValue(0)
        self.ui.bar_yag.setValue(0)

        #labellara bilgi yazdırıyoz
        self.ui.lbl_genel_durum.setText(f"Günlük Kalori İhtiyacı: {int(self.hedef_kalori)}" + " " + mesaj )

        #mor şerit ince kaldı kalınlaştırma işlemi
        self.ui.lbl_genel_durum.setMinimumHeight(50)
        #Butonlara işlevsellik kazandırıcaz

    def yemek_ekle(self):
        gelen_kalori = self.ui.spin_yemek_ekle.value()

        self.gunluk_kalori += gelen_kalori

        #barı güncelle
        self.ui.bar_kalori.setValue(int(self.gunluk_kalori))

        print(f"toplam kalori : {self.gunluk_kalori}")

    def protein_ekle(self):
        deger = self.ui.spin_protein_ekle.value()
        self.gunluk_protein += deger
        self.ui.bar_protein.setValue(int(self.gunluk_protein))

    def karbon_ekle(self):
        deger = self.ui.spin_karbon_ekle.value()
        self.gunluk_karbon += deger
        self.ui.bar_karbon.setValue(int(self.gunluk_karbon))

    def yag_ekle(self):
        deger = self.ui.spin_yag_ekle.value()
        self.gunluk_yag += deger
        self.ui.bar_yag.setValue(int(self.gunluk_yag))

    def spor_ekle(self):
        buton = self.sender()

        if buton == self.ui.btn_sinav_ekle:
            eklenecek = self.ui.spin_sinav_ekle.value()
            mevcut = self.ui.bar_sinav.value()
            self.ui.bar_sinav.setValue(mevcut + eklenecek)
            
        # Mekik
        elif buton == self.ui.btn_mekik_ekle:
            eklenecek = self.ui.spin_mekik_ekle.value()
            mevcut = self.ui.bar_mekik.value()
            self.ui.bar_mekik.setValue(mevcut + eklenecek)
            
        # Barfiks
        elif buton == self.ui.btn_barfiks_ekle:
            eklenecek = self.ui.spin_barfiks_ekle.value()
            mevcut = self.ui.bar_barfiks.value()
            self.ui.bar_barfiks.setValue(mevcut + eklenecek)
            
        # Koşu
        elif buton == self.ui.btn_kosu_ekle:
            eklenecek = self.ui.spin_kosu_ekle.value()
            mevcut = self.ui.bar_kosu.value()
            self.ui.bar_kosu.setValue(mevcut + eklenecek)

    #tebrik ediyorumm
    def hedef_kontrol(self):
        
        # 1. Mevcut ve Hedef Değerleri Al
        mevcut_kalori = self.ui.bar_kalori.value()
        hedef_kalori = self.ui.bar_kalori.maximum()
        
        # 2. Kontrol Et:
        if mevcut_kalori >= hedef_kalori and not self.tebrik_edildi:
            
            QMessageBox.information(self, "HELAL OLSUN! ", 
                                    "Tebrikler Şampiyon! Bugün de obeziteden bir adım uzaklaştın. \nSTAY HARD.\n"
                                    )
            
            
            self.tebrik_edildi = True




# ÇALIŞTIIIRRRRRRRRRRRR

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    pencere = DiyetisyenUygulamasi()
    pencere.show()
    sys.exit(app.exec_())
