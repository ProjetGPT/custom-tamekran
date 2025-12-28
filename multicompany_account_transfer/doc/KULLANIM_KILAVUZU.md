# Coatrans – Çok Şirketli Finans Yönetimi (Kullanım Kılavuzu)

Bu doküman, aşağıdaki 3 modül için **teknik olmayan kullanıcı** perspektifiyle hazırlanmıştır:

- `multicompany_account_transfer` (Multi Company Account Transfer)
- `purchase_order_type_journal` (Purchase Order Type Journal)
- `sale_order_type_journal` (Sale Order Type Journal)

## 1) Genel Ön Koşullar

- **Çoklu Şirket (Multi-Company)** kullanımınız aktif olmalıdır.
- Kullanıcınızın ilgili şirket(ler)e erişimi olmalıdır.
- Muhasebe tarafındaki menüler için genellikle **Muhasebe Yöneticisi** (Accounting Manager) yetkisi gerekir.

---

# A) Multi Company Account Transfer

## Amaç

Belirlenen bir muhasebe yevmiyesi (journal) üzerinden, **Kaynak Şirket**’te oluşan ve **onaylanan (Posted)** yevmiye kayıtlarını, otomatik olarak **Hedef Şirket**’te belirlenen hedef yevmiyeye kopyalamak/senkronlamak.

Bu sayede iki şirket arasında yevmiye hareketlerini standart ve kontrollü şekilde çoğaltabilirsiniz.

## 1) Kurulum / Ayar

### 1.1 Yevmiye (Journal) üzerinde senkron ayarı

- Menü:
  - **Muhasebe -> Yapılandırma -> Yevmiyeler** (Journals)
- Senkron yapmak istediğiniz yevmiyeyi açın.
- Yevmiye kartında **"Multi Company" (Çok Şirket)** sekmesine girin.
- Aşağıdaki alanları ayarlayın:

- **Senkron (Sync)**: Açık (ON)
- **Hedef Şirket (Destination Company)**: Hedef şirket
- **Hedef Yevmiye (Destination Journal)**: Hedef şirkette kullanılacak yevmiye

### 1.2 Önemli not (Hesap planı uyumu)

Kaynak ve hedef şirketin **hesap planı şablonunun (chart template)** uyumlu olması beklenir. Uyum yoksa sistem “Destination Company Account Chart Template Mismatch” benzeri bir uyarı verebilir.

## 2) Kullanım

Bu modül 2 farklı yerden takip/kullanım sağlar:

### 2.1 “Senkron bekleyen kayıtlar” listesini görmek

- Menü:
  - **Muhasebe -> Muhasebe -> Yevmiye Kayıtları** (Journal Entries) -> **Sync Journal Entries** (Senkron Yevmiye Kayıtları)
- Bu ekran, senkron ayarı açık yevmiyelerde oluşan ve henüz hedef şirkete aktarılmamış kayıtları listelemeye odaklıdır.
- Listede **Destination Move** (Hedef Kayıt) alanı doluysa, kayıt hedef şirkete aktarılmış demektir.

### 2.2 Toplu senkron (Wizard) çalıştırmak

Bu sihirbaz, seçtiğiniz şirket için belirli bir tarih aralığındaki **onaylanan (Posted)** kayıtları senkronlar.

- Menü:
  - **Ayarlar -> Kullanıcılar ve Şirketler -> Şirketler**
  - Kaynak şirketi açın
  - Üst menüdeki **Eylemler** (Actions) menüsünden **"Multi Company - Account Move Sync"** (Çok Şirket - Yevmiye Senkronu) çalıştırın

Sihirbaz alanları:

- **Kaynak Şirket (Source Company)**: Kaynak şirket
- **Başlangıç / Bitiş Tarihi (Date From / Date To)**: Senkronlanacak tarih aralığı
- **Senkron Kayıtlarını Sil (Sync Move Delete)**:
  - İşaretlenirse, aynı tarih aralığında daha önce hedef şirkete oluşturulmuş senkron kayıtlar silinip yeniden üretim yapılacak şekilde kullanılabilir.

Sonuç:

- İşlem sırasında sorun olursa **Error Log** sekmesinde hata listesi görünür.

## 3) İpuçları / Sık Karşılaşılan Durumlar

- Senkron yalnızca ilgili yevmiyede **Senkron (Sync) = Açık** ve hedef yevmiye tanımlıysa çalışır.
- Kayıtların senkron için **onaylanmış (Posted)** olması gerekir.
- Tarih aralığında beklediğiniz kayıtlar gelmiyorsa:
  - Kayıtların “Onaylandı (Posted)” durumunu kontrol edin.
  - Yevmiyenin “Multi Company” ayarlarını kontrol edin.
  - Tarih aralığını doğru girdiğinizden emin olun (gerekirse başlangıç/bitiş tarihlerini ters girmeyi deneyin).

---

# B) Purchase Order Type Journal

## Amaç

Satın alma siparişlerinde (Purchase Order) “**Tip (Type)**” seçimine göre, fatura (Vendor Bill) oluşturulurken kullanılacak **satın alma yevmiyesini (Purchase Journal)** otomatik belirlemek.

## 1) Kurulum / Ayar

### 1.1 Satın alma sipariş tiplerini oluşturma

- Menü:
  - **Satın Alma -> Yapılandırma -> Satın Alma Siparişi Tipleri** (Purchase Order Types)

Her tipte:

- **Ad (Name)**: Tip adı (örn. “İthalat”, “Yurtiçi”, “Hizmet”)
- **Yevmiye (Journal)**: Bu tip için kullanılacak **Satın Alma (Purchase)** türünde yevmiye
- **Varsayılan (Is Default)**: Varsayılan tip

Not:

- Aynı anda **yalnızca 1 adet** “Is Default” seçili tip olabilir.

## 2) Kullanım

### 2.1 Satın alma siparişinde tip seçimi

- Satın alma siparişi formunda “**Tip (Type)**” alanı görünür.
- Bu alan, sipariş taslak/teklif aşamalarında seçilebilir.

### 2.2 Fatura (Vendor Bill) oluşturma

- Satın alma siparişinden “Fatura Oluştur” adımı çalıştırıldığında:
  - Seçtiğiniz tipe bağlı **Yevmiye (Journal)**, oluşturulacak faturaya otomatik taşınır.

## 3) İpuçları / Sık Karşılaşılan Durumlar

- Tip seçili değilse veya tipte yevmiye tanımlı değilse, fatura oluştururken sistem standart davranışıyla devam eder.
- Varsayılan tip kuralı nedeniyle yeni bir tipe “Is Default” verirken hata alırsanız, önce mevcut varsayılan tipi kapatın.

---

# C) Sale Order Type Journal

## Amaç

Satış tarafında:

- Satış siparişi üzerinde **Tip (Type)** seçimi yapabilmek
- Satış Ekibi (Sales Team) bazında satış yevmiyesi (Sales Journal) tanımlayabilmek
- Fatura oluşturma sihirbazında doğru **Sales Journal**’ın otomatik gelmesini sağlamak

## 1) Kurulum / Ayar

### 1.1 Satış sipariş tiplerini tanımlama

- Menü:
  - **Satış -> Yapılandırma -> Satış Siparişi Tipleri** (Sale Order Types)

Alanlar:

- **Ad (Name)**
- **Yevmiye (Journal)** (Satış/Sales türünde)
- **Varsayılan (Is Default)**

Not:

- Burada da aynı anda **yalnızca 1 adet** varsayılan tip seçilebilir.

### 1.2 Satış Ekibi (Sales Team) üzerinde yevmiye tanımlama

- Menü:
  - **Satış -> Yapılandırma -> Satış Ekipleri** (Sales Teams)
- İlgili satış ekibinde **Yevmiye (Journal)** alanını doldurun.

## 2) Kullanım

### 2.1 Satış siparişinde tip seçimi

- Satış siparişi formunda “**Tip (Type)**” alanı görünür ve seçilebilir.

### 2.2 Fatura oluşturma (Advance Payment / Invoice Orders wizard)

- Satış siparişi üzerinde “Fatura Oluştur” adımında açılan sihirbazda **Yevmiye (Journal)** alanı görünür.
- Sistem varsayılan olarak şu sırayla yevmiye seçmeye çalışır:

1. Siparişin **Satış Ekibi (Sales Team)** üzerinde tanımlı yevmiye
2. Yoksa, şirketin ilk uygun **Satış (Sales)** yevmiyesi

- İsterseniz sihirbazda **Yevmiye (Journal)** alanını elle değiştirerek faturalamanın hangi yevmiyeden yapılacağını belirleyebilirsiniz.

## 3) İpuçları / Sık Karşılaşılan Durumlar

- Sihirbazda beklediğiniz yevmiye gelmiyorsa önce satış ekibindeki “Yevmiye (Journal)” alanını kontrol edin.
- Şirkette Satış (Sales) türünde yevmiye yoksa seçim yapılamaz; muhasebe yapılandırmasından satış yevmiyesi oluşturulmalıdır.

---

## Ek: Kullanıcı için kısa özet

- **Satın alma tarafı**: Satın alma siparişi üzerinde “Tip” seç -> Fatura doğru satın alma yevmiyesinden gelir.
- **Satış tarafı**: Satış Ekibi’ne yevmiye tanımla -> Fatura sihirbazı doğru satış yevmiyesini otomatik getirir.
- **Çok şirketli muhasebe senkronu**: Yevmiye üzerinde hedef şirket/yevmiye tanımla -> Şirket ekranından sihirbazı çalıştır -> Onaylanmış kayıtlar hedef şirkete kopyalanır.
