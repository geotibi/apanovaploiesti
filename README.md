![logoANB](https://github.com/user-attachments/assets/dbf1a8c1-7c53-41f3-98b2-a61be7e16dde)
# Apa Nova Ploiești - Integrare pentru Home Assistant!
Această integrare oferă monitorizare completă a datelor contractuale disponibile pentru utilizatorii Apa Nova Ploiești România. Integrarea se poate configura prin interfața UI și permite afișarea diferitelor date disponibile în contul de utilizator. 🚀
🌟 # Caracteristicile senzorilor
**Senzorul `Clor`**
  - Afișează cantitatea de clor din apă

**Senzorul `Cod Client`**
  - Afișează codul de client

**Senzorii `Dată Emitere, Dată Plată, Dată Scadență`**
  - Afișează data de emitere a ultimei facturi, data când a fost plătită (dacă factura nu a fost achitată va afișa valoarea "0000-00-00") și data scadentă a ultimei facturi

**Senzorul `Număr Factură`**
  - Afișează numărul ultimei facturi

**Senzorul `pH`**
  - Afișează pH-ul apei din zonă

**Senzorul `Sector`**
  - Afișează sectorul/zona Nord-EST

**Senzorul `Sold`**
  - Afișează soldul de la ultima factură

**Senzorul `Status Factură`**
  - **🔍 Monitorizare:**
    - Afișează dacă ultima factură este Achitată sau Neachitată
  - **📊 Atribute disponibile:**
    - Istoricul facturilor din cont

**Senzorul `Total`**
  - Afișează totalul de plată

# ⚙️Configurare

**🛠️Interfața UI**
1. Adaugă integrarea din meniul **Setări > Dispozitive și Servicii > Adaugă Integrare.**
2. Introdu datele contului ApaNova Ploiești:
     - **Username:** username-ul contului tău ApaNova
     - **Password:** parola contului tău ApaNova
     - **Cod client:** codul de client aferent contului tău ApaNova

# 🚀Instalare
**💡 Instalare prin HACS:**
1. Adaugă [depozitul personalizat](https://github.com/geotibi/apanovaploiesti) în HACS.🛠️
2. Caută integrarea ApaNova Ploiești și instaleaz-o. ✅
3. Repornește Home Assistant și configurează integrarea. 🔄

**✋ Instalare manuală:**
1. Clonează sau descarcă [depozitul GitHub](https://github.com/geotibi/apanovaploiesti). 📂
2. Copiază folderul custom_components/apanovaploiesti în directorul custom_components al Home Assistant. 🗂️
3. Repornește Home Assistant și configurează integrarea. 🔄

# ✨ Exemple de utilizare
<h3>🔔 Automatizare pentru avertizare neplată cu o zi înainte de data scadentă:</h3>

Un exemplu de automatizare pe care o poți crea pentru a nu uita de plata facturii.

```bash
alias: Notificare factura Apa Nova
description: Notificare cu o zi înainte de data scadență
triggers:
  - trigger: template
    value_template: >
      {% set due_date = states('sensor.apanova_ploiesti_data_scadenta') %} {% if
      due_date != 'unknown' and due_date != '' %}
        {{ (as_datetime(due_date) - now()).days == 1 }}
      {% else %}
        false
      {% endif %}
actions:
  - action: notify.mobile_app_sm_g975f
    metadata: {}
    data:
      message: Mâine este ultima zi de plată a facturii tale Apa Nova
      title: Notificare Factură Apa Nova
mode: single
```

<h3>🔍 Card pentru afișsarea datelor în Dashboard:</h3>

Un exemplu de cum se pot afișa datele în dashboard.

```bash
type: entities
title: Apa Nova Ploiești
entities:
  - entity: sensor.apanova_ploiesti_clor
    name: Cantitate clor în apă
  - entity: sensor.apanova_ploiesti_cod_client
    name: Cod client
  - entity: sensor.apanova_ploiesti_data_emitere
    name: Dată emitere ultima factură
  - entity: sensor.apanova_ploiesti_data_plata
    name: Dată plată ultima factură emisă
  - entity: sensor.apanova_ploiesti_data_scadenta
    name: Dată scadență ultima factură emisă
  - entity: sensor.apanova_ploiesti_numar_factura
    name: Numărul ultimei facturi emise
  - entity: sensor.apanova_ploiesti_ph
    name: pH-ul apei
  - entity: sensor.apanova_ploiesti_sector
    name: Sector/zonă
  - entity: sensor.apanova_ploiesti_sold
    name: Sold-ul ultimei facturi emise
  - entity: sensor.apanova_ploiesti_status_factura
    name: Statusul ultimei facturi emise
  - entity: sensor.apanova_ploiesti_total
    name: Total de plată
```

![image](https://github.com/user-attachments/assets/d4ea09f7-771c-4de2-8338-54b5cfe7d89f)



# ☕ Susține dezvoltatorul
Dacă îți place această integrare și vrei să sprijini efortul depus, **Buy me a coffee**

<a href="https://www.buymeacoffee.com/geotibi" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

Mulțumesc

## Contribuții

Contribuțiile sunt întotdeauna binevenite! Simte-te liber să vii cu idei noi de îmbunătățire sau să raportezi probleme [aici](https://github.com/geotibi/apanovaploiesti/issues).

# 🔰Suport
Dacă îți place această integrare, oferă-i o ⭐ pe [GitHub](https://github.com/geotibi/apanovaploiesti/)! 🙏
