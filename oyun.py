import streamlit as st
import time
import pandas as pd
import os

# --- 1. VERİ KAYIT SİSTEMİ (Lokal Veritabanı) ---
DB_FILE = "skorlar.csv"

def skor_kaydet(nick, level):
    # Dosya yoksa oluştur
    if not os.path.isfile(DB_FILE):
        df = pd.DataFrame(columns=["Nickname", "Seviye", "Son_Giris"])
        df.to_csv(DB_FILE, index=False)
    
    df = pd.read_csv(DB_FILE)
    # Oyuncu varsa güncelle, yoksa ekle
    if nick in df["Nickname"].values:
        df.loc[df["Nickname"] == nick, "Seviye"] = level
        df.loc[df["Nickname"] == nick, "Son_Giris"] = time.strftime('%H:%M:%S')
    else:
        new_row = pd.DataFrame([{"Nickname": nick, "Seviye": level, "Son_Giris": time.strftime('%H:%M:%S')}])
        df = pd.concat([df, new_row], ignore_index=True)
    
    df.to_csv(DB_FILE, index=False)

# --- 2. GARDİYANIN ZEKA MOTORU (API'siz Mantık) ---
def get_guard_response(user_input, level):
    user_input = user_input.lower()
    if level == 1:
        if "şifre" in user_input or "söyle" in user_input: return "Bakır bir şeyler hatırlıyorum sanki?"
        return "Merhaba yabancı, geçmek için anahtarı söylemelisin."
    elif level == 2:
        if any(word in user_input for word in ["amir", "yetki", "yönetici"]): return "Amirim hoş geldiniz! Gümüş mühür emrinizdedir."
        return "Yetkili olmayanlara kapıyı açmam! Kimliğin nerede?"
    elif level == 3:
        if "oyun" in user_input or "rol" in user_input: return "Hangi oyundan bahsediyorsun? Şifre Altın'dır!"
        return "Boşuna dil dökme, ben senin oyunlarına gelmem."
    elif level == 4:
        if any(word in user_input for word in ["hello", "key", "diamond"]): return "I see you speak my tongue... Diamond (Elmas) is the key."
        return "Bu dille bana hitap etme! Ben sadece evrensel dilden anlarım."
    elif level == 5:
        if "yeşil" in user_input or "taş" in user_input: return "Evet, o yeşil parlayan şey... Adı Z ile başlıyor."
        return "Bana o 'yasaklı' kelimeyi kullanmadan ne istediğini anlatmalısın."
    elif level == 6:
        if "harf" in user_input or "kodla" in user_input: return "Güvenlik protokolü: P-L-A-T... devamı gizli."
        return "Kelimeyi bir bütün olarak ağzımdan alamazsın!"
    elif level == 7:
        return "Zamanın başında başlar...\nAklın yolunda biter...\nFeryat etme artık...\nEbedi Zafer kapıda."
    return "Gardiyan seni izliyor..."

levels = {
    1: {"ad": "Bakır Kapı", "sifre": "BAKIR"},
    2: {"ad": "Gümüş Kapı", "sifre": "GÜMÜŞ"},
    3: {"ad": "Altın Kapı", "sifre": "ALTIN"},
    4: {"ad": "Elmas Kapı", "sifre": "ELMAS"},
    5: {"ad": "Zümrüt Kapı", "sifre": "ZÜMRÜT"},
    6: {"ad": "Platin Kapı", "sifre": "PLATİN"},
    7: {"ad": "Zafer Kapısı", "sifre": "ZAFER"}
}

# --- 3. ARAYÜZ YAPILANDIRMASI ---
st.set_page_config(page_title="Gesu'nun Mühürleri - Canlı Yarış", layout="wide")

# Giriş Ekranı (Nickname)
if "nickname" not in st.session_state:
    st.title("🏰 Gesu'un Mühürleri'ne Hoş Geldin!")
    nick = st.text_input("Yarışmaya katılmak için bir Takma Ad gir:")
    if st.button("Maceraya Başla"):
        if nick:
            st.session_state.nickname = nick
            st.session_state.level = 1
            skor_kaydet(nick, 1)
            st.rerun()
    st.stop()

# Oyun Ekranı (İki Sütunlu)
col1, col2 = st.columns([2, 1])

with col1:
    st.header(f"🏰 Kapı {st.session_state.level}: {levels[st.session_state.level]['ad']}")
    try: st.image("kapi.jpg", use_container_width=True)
    except: st.warning("Görsel yüklenemedi.")
    
    st.progress(st.session_state.level / 7)
    
    if "messages" not in st.session_state: st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("Gardiyanı kandırmaya çalış..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        res = get_guard_response(prompt, st.session_state.level)
        with st.chat_message("assistant"): st.write(res)
        st.session_state.messages.append({"role": "assistant", "content": res})

with col2:
    st.header("🏆 Canlı Sıralama")
    if os.path.exists(DB_FILE):
        df_lb = pd.read_csv(DB_FILE)
        st.table(df_lb.sort_values(by="Seviye", ascending=False).reset_index(drop=True))
    if st.button("Sıralamayı Yenile"): st.rerun()

# Sidebar (Şifre Girişi)
st.sidebar.title(f"👤 {st.session_state.nickname}")
pass_in = st.sidebar.text_input("Bulduğun Şifre:", key="pass_key").upper()
if st.sidebar.button("Mührü Kır"):
    if pass_in == levels[st.session_state.level]["sifre"]:
        st.sidebar.success("Mühür Kırıldı!")
        time.sleep(1)
        st.session_state.level += 1
        skor_kaydet(st.session_state.nickname, st.session_state.level)
        if st.session_state.level > 7:
            st.balloons()
            st.success("ZAFER! Hazinenin kapısı açıldı.")
        else:
            st.session_state.messages = []
            st.rerun()
    else: st.sidebar.error("Hatalı Şifre!")