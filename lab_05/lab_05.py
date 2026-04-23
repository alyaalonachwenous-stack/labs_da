import streamlit as st
import pandas as pd
import os
import urllib.request
from datetime import datetime
import matplotlib.pyplot as plt 
import seaborn as sns

@st.cache_resource
def download_vhi_data(): #функція для завантаження даних 
    os.makedirs("vhi_data", exist_ok=True)

    existing = os.listdir("vhi_data")
    for i in range(1, 28):
        if any(f"vhi_id_{i}_" in filename for filename in existing):
               continue
        else:
            now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"vhi_data/vhi_id_{i}_{now}.csv"
            vhiurl = f"https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?country=UKR&provinceID={i}&year1=1981&year2=2024&type=Mean"

            urllib.request.urlretrieve(vhiurl, filename)
download_vhi_data()

@st.cache_data
def cleaning_df_data(): #функція для очищення даних
    all_dfs = []
    headers = ['Year', 'Week', 'SMN', 'SMT', 'VCI', 'TCI', 'VHI', 'empty']

    for filename in os.listdir("vhi_data"):
        filepath = f"vhi_data/{filename}"
        id_prov = int(filename.split('_')[2])
        df_temp = pd.read_csv(filepath, header=None, skiprows=2, names=headers)
        df_temp['province'] = id_prov
        df_temp = df_temp.drop('empty', axis=1)
    
        all_dfs.append(df_temp)
    
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df['Year'] = final_df['Year'].astype(str).str.replace('<tt><pre>', '', regex=False)
    final_df['Year'] = final_df['Year'].astype(str).str.replace('</pre>', '', regex=False)
    final_df['Year'] = pd.to_numeric(final_df['Year'], errors='coerce')
    final_df = final_df.dropna()
    final_df['Year'] = final_df['Year'].astype(int)
    final_df['Week'] = final_df['Week'].astype(int)
    final_df = final_df[final_df['VHI'] >= 0]

    ua_provinces = {
        1: 'Черкаська', 2: 'Чернігівська', 3: 'Чернівецька', 4: 'Крим', 
        5: 'Дніпропетровська', 6: 'Донецька', 7: 'Івано-Франківська', 
        8: 'Харківська', 9: 'Херсонська', 10: 'Хмельницька', 11: 'Київська', 
        12: 'м. Київ', 13: 'Кіровоградська', 14: 'Луганська', 15: 'Львівська', 
        16: 'Миколаївська', 17: 'Одеська', 18: 'Полтавська', 19: 'Рівненська', 
        20: 'Севастополь', 21: 'Сумська', 22: 'Тернопільська', 23: 'Закарпатська', 
        24: 'Вінницька', 25: 'Волинська', 26: 'Запорізька', 27: 'Житомирська'
    }
    final_df['province'] = final_df['province'].replace(ua_provinces)

    return final_df
df = cleaning_df_data()

#тут блок, у якому я визначаю потрібні випадаючі списки 
if 'index_choice' not in st.session_state:
    st.session_state['index_choice'] = 'VHI'

selected_index = st.sidebar.selectbox( 
     label = "оберіть часовий ряд",
     options = ['VCI', 'TCI', 'VHI'],
     key='index_choice'
     )

if 'province_choice' not in st.session_state:
    st.session_state['province_choice']= 'Сумська'

selected_province = st.sidebar.selectbox(
    label = 'оберіть область',
    options = df['province'].unique(),
    key = 'province_choice'
)

#тут блок, де я визначаю потрібні слайдери
if 'years_range' not in st.session_state:
    st.session_state['years_range'] = (int(df['Year'].min()), int(df['Year'].max()))

selected_years = st.sidebar.slider(
    label = "виберіть інтервал років:",
    min_value = int(df['Year'].min()),
    max_value = int(df['Year'].max()),
    value = st.session_state['years_range'], 
    key = 'years_range'                      
)

if 'weeks_range' not in st.session_state:
    st.session_state['weeks_range'] = (1, 52)

selected_weeks = st.sidebar.slider(
    label = 'виберіть інтервал тижнів',
    min_value = 1,
    max_value = 52,
    value = st.session_state['weeks_range'],
    key = 'weeks_range'
)

#функція для кнопки скидання та сама кнопка скидання
def reset_filters():
    st.session_state['index_choice'] = 'VHI'
    st.session_state['province_choice'] = 'Сумська'
    st.session_state['years_range'] = (int(df['Year'].min()), int(df['Year'].max()))
    st.session_state['weeks_range'] = (1, 52)
    st.session_state['asc_key'] = False
    st.session_state['desc_key'] = False

st.sidebar.button("Скинути всі фільтри", on_click=reset_filters)

#функція, яка створює копію оригінального фрейму та фільтрує його відповідно до вибраних значень на слайдерах та списках. 
#використовується для другої вкладки, де показано лише вибрану область
def filter_values(df, selected_province, selected_years, selected_weeks, selected_index):
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df['province'] == selected_province]
    min_year = selected_years[0]
    max_year = selected_years[1]
    filtered_df = filtered_df[(filtered_df['Year'] >= min_year)&(filtered_df['Year'] <= max_year)]
    min_week = selected_weeks[0]
    max_week = selected_weeks[1]
    filtered_df = filtered_df[(filtered_df['Week'] >= min_week)&(filtered_df['Week'] <= max_week)]
    filtered_df = filtered_df[['province', 'Year', 'Week', selected_index]]

    return filtered_df

ready_df = filter_values(df, selected_province, selected_years, selected_weeks, selected_index)

#функція для третьої вкладки, фільтрує дані всіх областей за вибраними значеннями
def filter_all_provinces(df, selected_years, selected_weeks, selected_index):
    filtered_df = df.copy()
    
    min_year = selected_years[0]
    max_year = selected_years[1]
    filtered_df = filtered_df[(filtered_df['Year'] >= min_year) & (filtered_df['Year'] <= max_year)]
    
    min_week = selected_weeks[0]
    max_week = selected_weeks[1]
    filtered_df = filtered_df[(filtered_df['Week'] >= min_week) & (filtered_df['Week'] <= max_week)]
    
    filtered_df = filtered_df[['province', 'Year', 'Week', selected_index]]
    
    return filtered_df

all_data_df = filter_all_provinces(df, selected_years, selected_weeks, selected_index)

#тут блок із чекбоксами для сортування за зростанням і спаданням. пррописані умови якщо увімкнений кожен чекбокс
#також є дві функції, які відповідають за поведінку чекбоксів, якщо вони обидва True, реалізовано взаємовиключення
#тобто, обидва чекбокси не можуть бути True одночасно, якщо один True - він вимикає інший
def disable_desk():
    if st.session_state["asc_key"] == True:
        st.session_state["desc_key"] = False

def disable_asc():
    if st.session_state["desc_key"] == True:
        st.session_state["asc_key"] = False

st.sidebar.checkbox(
    label = 'сортувати за зростанням',
    key = "asc_key",
    on_change = disable_desk
)

st.sidebar.checkbox(
    label = "сортувати за спаданням",
    key = 'desc_key',
    on_change= disable_asc
)

if st.session_state["asc_key"] == True:
    ready_df = ready_df.sort_values(by=selected_index, ascending=True)
elif st.session_state["desc_key"] == True:
    ready_df = ready_df.sort_values(by=selected_index, ascending=False)

#тут прописані вкладки
tab1, tab2, tab3 = st.tabs(["таблиця", "графік динаміки", "порівняння областей"])

with tab1: #просто виводимо відфільтровану табличку
    st.header("відфільтровані дані")
    st.dataframe(ready_df, use_container_width=True)

with tab2: #тут виводиться графік за відфльтрованою таблицею
    st.header('графік відображення даних')
    ready_df['Year_Week'] = ready_df['Year'].astype(str) + '-' + ready_df['Week'].astype(str).str.zfill(2)
    ready_df = ready_df.sort_values(by='Year_Week')

    st.header(f'розподіл {selected_index} для області {selected_province}')
    fig, ax = plt.subplots(figsize=(15,6))

    ax.plot(ready_df['Year_Week'], ready_df[selected_index], color='dodgerblue', linewidth=2)

    ax.set_xlabel('рік та тиждень')
    ax.set_ylabel(f'індекс {selected_index}')
    ax.grid(axis='both', linestyle='--', alpha=0.5)

    step = max(1, len(ready_df) // 15)
    ax.set_xticks(ax.get_xticks()[::step])

    min_idx = ready_df[selected_index].idxmin()
    max_idx = ready_df[selected_index].idxmax()
    min_row = ready_df.loc[min_idx]
    max_row = ready_df.loc[max_idx]

    #тут реалізовано візуальний показ мінімального та максимального значення за заданий період(для пункту про вигляд графіку)
    ax.scatter(min_row['Year_Week'], min_row[selected_index], color='red', s=80, zorder=5)
    ax.scatter(max_row['Year_Week'], max_row[selected_index], color='green', s=80, zorder=5)
    ax.annotate(f"Мінімум: {min_row[selected_index]:.2f}", 
                xy=(min_row['Year_Week'], min_row[selected_index]), 
                xytext=(0, -20), textcoords="offset points", 
                ha='center', color='red', fontweight='bold')
                
    ax.annotate(f"Максимум: {max_row[selected_index]:.2f}", 
                xy=(max_row['Year_Week'], max_row[selected_index]), 
                xytext=(0, 10), textcoords="offset points",  
                ha='center', color='green', fontweight='bold')
    
    #тут реалізовано функціонал показу історичної норми області через чекбокс. чекбокс знаходиться лише в цій вкладці
    #для того, щоб не засмічувати основний сайдбар, бо саме цей чекбокс потрібен лише тут
    show_norm = st.checkbox("показати історичну норму області")
    if show_norm:
        norm_val = df[df['province'] == selected_province][selected_index].mean()
        ax.axhline(y = norm_val, color = 'orange', linestyle = '--', linewidth = 2, label=f'норма ({norm_val:.2f})')
        ax.legend()

    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

with tab3: #тут виводиться графік порівняння зі всіма областями
    st.header('порівняння з іншими областями')
    all_data_df['Year_Week'] = all_data_df['Year'].astype(str) + '-' + all_data_df['Week'].astype(str).str.zfill(2)
    all_data_df = all_data_df.sort_values(by='Year_Week')

    fig, ax = plt.subplots(figsize=(15,6))
    unique_provinces = all_data_df['province'].unique()

    for prov in unique_provinces:
        prov_data = all_data_df[all_data_df['province'] == prov]
        ax.plot(prov_data['Year_Week'], prov_data[selected_index], color='grey', alpha=0.2, linewidth=1) #усі області, крім обраної, сірі

    ax.plot(ready_df['Year_Week'], ready_df[selected_index], color='red', linewidth=3, label=selected_province) #обрана область червона
    ax.set_xlabel('рік та тиждень')
    ax.set_ylabel(f'Індекс {selected_index}')
    ax.legend() 
    ax.grid(axis='both', linestyle='--', alpha=0.5)

    step = max(1, len(ready_df) // 15)
    if len(ax.get_xticks()) > 0:
        ax.set_xticks(ax.get_xticks()[::step])
    plt.xticks(rotation=45, ha='right')
    
    #тут реалізовано функціонал, за яким можна обрати одну конкретну область для порівняння, використано випадаючий список
    if 'competitor' not in st.session_state:
        st.session_state['competitor'] = 'Київська'

    selected_competitor = st.selectbox(
        label = 'оберіть область для порівняння',
        options = ['немає'] + list(df['province'].unique()),
        key = 'competitor'
    )

    if selected_competitor != 'немає':
        comp_data = all_data_df[all_data_df['province'] == selected_competitor]
        ax.plot(comp_data['Year_Week'], comp_data[selected_index], color = 'blue', linewidth = 3, label = selected_competitor)
    
    st.pyplot(fig)