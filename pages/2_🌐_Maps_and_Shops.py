import streamlit as st
import pandas as pd
import json
import plotly.express as px
from geopy.distance import geodesic

# PAGE CONFIG

st.set_page_config(page_title='Магазины и регионы')

# LOADING AND CREATING DATA

folder = '/app/demo_app_in_streamlit/pages/files'

with open(folder + 'some_goods_sales_regions.json', encoding='utf-8') as file:
    region_sales_json = json.load(file)

with open(folder + 'some_goods_sales_kazan_shops_my_numbers.json', encoding='utf-8') as file:
    kazan_sales_json = json.load(file)

with open(folder + 'russia_with_crimea(click_that_hood)_my_version_ruschars_without_gaps.json',
          encoding='utf-8') as file:
    russian_regions_json = json.load(file)

shops_addresses_kazan = pd.read_csv(folder + 'Все_Адреса_Казань_для_демо(с координатами).csv', encoding='utf-8')


def fill_dfs_dct(jsn):
    dct = dict()
    for df_name in jsn:
        dct[df_name] = pd.read_json(jsn[df_name])
    return dct


dfs_region_sales = fill_dfs_dct(region_sales_json)
dfs_kazan_sales = fill_dfs_dct(kazan_sales_json)

products_lst = ['Laimon Fresh',
                'Laimon Fresh Mango',
                '7 up',
                '7 up Mojito',
                '7 up Lemon-Lemon',
                'Sprite',
                'Sprite Ice',
                'Sprtie Ice Zero',
                'Arctic']

metrics_lst = ['Продажи, шт', 'Продажи, руб с НДС', 'Продажи, л']

cats_dct_for_carbonated = {'БАН': 'ban', 'Газированная вода': 'carbonated'}
cats_dct_for_water = {'БАН': 'ban', 'Вода': 'water'}

products_dct = {'Laimon Fresh': 'laimon_fresh',
                'Laimon Fresh Mango': 'laimon_fresh_mango',
                '7 up': 'seven_up',
                '7 up Mojito': 'seven_up_mojito',
                '7 up Lemon-Lemon': 'seven_up_lemon_lemon',
                'Sprite': 'sprite',
                'Sprite Ice': 'sprite_ice',
                'Sprtie Ice Zero': 'sprite_ice_zero',
                'Arctic': 'arctic'}


# MAP FUNCTIONS

## Map by Regions


def map_of_region(df):
    fig = px.choropleth_mapbox(df, geojson=russian_regions_json, locations='Область',
                               featureidkey='properties.name',
                               color=metric_of_regions,
                               color_continuous_scale="Reds",
                               mapbox_style="carto-positron",
                               center={'lat': 68, 'lon': 105},
                               zoom=1.1,
                               opacity=0.5,
                               )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


## Kazan's shops


def map_shops_kazan():
    fig = px.scatter_mapbox(shops_addresses_kazan,
                            lat='lat',
                            lon='long',
                            mapbox_style='carto-positron',
                            color='Название сети',
                            zoom=9,
                            hover_name=pd.Series(shops_addresses_kazan['Название сети'] +
                                                 " №" + shops_addresses_kazan['Номер магазина в сети'].astype(str)),
                            hover_data={'Название сети': False,
                                        'lat': False,
                                        'long': False}
                            )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


## Sales of Kazan's shops


def map_kazan_sales(df, zoom):
    fig = px.scatter_mapbox(df,
                            lat='lat',
                            lon='long',
                            mapbox_style='carto-positron',
                            color='Название сети',
                            zoom=zoom,
                            size=metric_of_kazan,
                            hover_name=pd.Series(df['Название сети'] + " №" + df['Номер магазина в сети'].astype(str)),
                            hover_data={'Название сети': False,
                                        'lat': False,
                                        'long': False}
                            )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


# BODY


## Head


st.title('Метрики по регионам России и магазинам Казани (для примера)')

st.caption(':red[ВНИМАНИЕ! Данные, представленные на этом сайте, выдуманы и носят  исключительно демонстрационный \
характер. Все совпадения с реальностью случайны.]')

st.header('Период: Январь 2023')


## Sales in regions


st.header('Продажи по регионам')

col11, col12 = st.columns(2)

with col11:
    product_of_regions = st.selectbox('Выберите продукт из списка ниже:', products_lst)
    col_name_of_regions_product = products_dct[product_of_regions]

with col12:
    metric_of_regions = st.selectbox('Выберите метрику:', metrics_lst)

# st.subheader(f"Продукт: {product_of_regions}")

### Sales in regions chart

st.plotly_chart(map_of_region(dfs_region_sales[col_name_of_regions_product]))

### Top-5 regions by sales (table)

region_df_for_table = dfs_region_sales[col_name_of_regions_product] \
    .drop(index=0).sort_values(metric_of_regions, ascending=False).head(5)

number_style = lambda x: '{0:,}'.format(x).replace(',', ' ')

st.subheader('Топ-5 регионов по продажам')
st.dataframe(region_df_for_table.style.format({'Продажи, шт': number_style,
                                               'Продажи, руб с НДС': number_style,
                                               'Продажи, л': number_style}),
             hide_index=True)


## Sales in Kazan


st.header('Продажи в магазинах Казани')
st.subheader('Адреса всех магазинов')

st.plotly_chart(map_shops_kazan())

st.subheader('Продажи по магазинам Казани')
col21, col22 = st.columns(2)

with col21:
    product_of_kazan = st.selectbox('Выберите продукт:', products_lst)
    col_name_of_kazan_product = products_dct[product_of_kazan]

with col22:
    metric_of_kazan = st.selectbox('Выберите метрику:', metrics_lst, key=4)

if len(dfs_kazan_sales[col_name_of_kazan_product]):

    ### Chart:

    df_for_kazan_sales = dfs_kazan_sales[col_name_of_kazan_product]
    st.plotly_chart(map_kazan_sales(df_for_kazan_sales, 9))

    ### Table (top-5)

    kazan_df_for_table = df_for_kazan_sales \
        .drop(index=0, columns=['lat', 'long', 'gps']) \
        .sort_values(metric_of_kazan, ascending=False) \
        .head(5)

    number_style = lambda x: '{0:,}'.format(x).replace(',', ' ')

    st.subheader(f'Топ-5 Магзинов Казани по продажам {product_of_kazan}')
    st.dataframe(kazan_df_for_table.style.format({'Продажи, шт': number_style,
                                                  'Продажи, руб с НДС': number_style,
                                                  'Продажи, л': number_style}),
                 column_config={'Продажи, л': 'Продажи, л'},
                 hide_index=True)


else:
    st.warning('Данный товар не был продан ни в одном из магазинов г. Казань в январе 2023 года.')

### Shops around

st.subheader('Продажи в близжаших магазинах (в заданной окрестности от выбранного)')

col31, col32, col33 = st.columns(3)

with col31:
    product_of_shop = st.selectbox('Выберите продукт:', products_lst, key=5)
    col_name_of_shop_product = products_dct[product_of_kazan]
    temp_df_for_shops_around = dfs_kazan_sales[col_name_of_shop_product]

with col32:
    net = st.selectbox('Выберите сеть:', dfs_kazan_sales[col_name_of_shop_product]['Название сети'].unique())

with col33:
    shop_number = st.selectbox('Номер магазина в сети:',
                               temp_df_for_shops_around[temp_df_for_shops_around['Название сети'] == net]
                               ['Номер магазина в сети'].unique())
    shop = temp_df_for_shops_around[(temp_df_for_shops_around['Название сети'] == net) &
                                    (temp_df_for_shops_around['Номер магазина в сети'] == shop_number)]
    shop_coord = shop.gps.squeeze()

radius = st.number_input('Введите максимальное расстояние до другого магазина, км:',
                         value=0.5,
                         step=0.1,
                         min_value=0.0,
                         max_value=100.0)

df_for_shops_around = temp_df_for_shops_around[temp_df_for_shops_around.gps.apply(
    lambda x: geodesic(x, shop_coord).kilometers <= radius)]

### Chart

st.plotly_chart(map_kazan_sales(df_for_shops_around, 12))

### Table

shops_around_df_for_table = df_for_shops_around \
    .drop(columns=['lat', 'long', 'gps']) \
    .sort_values('Продажи, руб с НДС', ascending=False)

st.write(f'**Список магазинов в радиусе {radius} км в порядке убывания по количеству продаж в рублях\*:**')
st.caption('\* если другой порядок не определен пользователем (по щелчку мыши на названии столбца в таблице))')
st.dataframe(shops_around_df_for_table.style.format({'Продажи, шт': number_style,
                                                     'Продажи, руб с НДС': number_style,
                                                     'Продажи, л': number_style}),
             hide_index=True)
