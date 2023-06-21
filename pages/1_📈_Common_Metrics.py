import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# PAGE CONFIG

st.set_page_config(page_title='Общие метрики по продукту')

# Loading and creating data

folder = '/app/demo_app_in_streamlit/pages/files/'

met_df = pd.read_csv(folder + 'df_for_met_and_pie.csv', index_col=0)
delta_met_df = pd.read_csv(folder + 'delta_df_for_met_and_pie.csv', index_col=0)
week_sales = pd.read_csv(folder + 'week_sales_df.csv', index_col=0)

products_lst = ['Laimon Fresh',
                'Laimon Fresh Mango',
                '7 up',
                '7 up Mojito',
                '7 up Lemon-Lemon',
                'Sprite',
                'Sprite Ice',
                'Sprtie Ice Zero',
                'Arctic']

cats_dct_for_carbonated = {'БАН': 'ban', 'Газированная вода': 'carbonated'}
cats_dct_for_water = {'БАН': 'ban', 'Вода': 'water'}


def create_products_dct():
    dct = dict()
    for i, product in enumerate(products_lst):
        dct[product] = met_df.iloc[:, 3:].columns[i]
    return dct


products_dct = create_products_dct()


# Charts Function


def three_plots(df):
    fig = make_subplots(rows=1, cols=3, specs=[[{'type': 'domain'}, {'type': 'domain'}, {'type': 'domain'}]])

    labels = [product_of_page, 'Остальные товары']
    v1 = [df.loc['pieces', col_name_of_page_product], \
          int(df.loc['pieces', cats_col_name] - df.loc['pieces', col_name_of_page_product])]
    v2 = [df.loc['rub', col_name_of_page_product], \
          df.loc['rub', cats_col_name] - df.loc['rub', col_name_of_page_product]]
    v3 = [df.loc['volume', col_name_of_page_product], \
          df.loc['volume', cats_col_name] - df.loc['volume', col_name_of_page_product]]

    # Create subplots: use 'domain' type for Pie subplot
    fig.add_trace(go.Pie(labels=labels, values=v1, name="",
                         hovertemplate=
                         '%{label}' +
                         '<br>' + '%{value:,} шт' +
                         '<br>' + '%{percent}'
                         ),
                  1, 1)
    fig.add_trace(go.Pie(labels=labels, values=v2, name="",
                         hovertemplate=
                         '%{label}' +
                         '<br>' + '%{value:,} руб.' +
                         '<br>' + '%{percent}'
                         ),
                  1, 2)
    fig.add_trace(go.Pie(labels=labels, values=v3, name="",
                         hovertemplate=
                         '%{label}' +
                         '<br>' + '%{value:,} л' +
                         '<br>' + '%{percent}'
                         ),
                  1, 3)

    # Use `hole` to create a donut-like pie chart
    fig.update_traces(hole=.4)
    fig.update_layout(
        # Add annotations in the center of the donut pies.
        annotations=[dict(text='шт.', x=0.115, y=0.5, font_size=24, showarrow=False),
                     dict(text='₽', x=0.5, y=0.5, font_size=24, showarrow=False),
                     dict(text='л.', x=0.88, y=0.5, font_size=24, showarrow=False)])

    return fig


def many_products_scatter_line(incomplete_weeks, *args):
    if incomplete_weeks:
        df = week_sales
        nticks = 6
    else:
        df = week_sales.iloc[1:-1, :]
        nticks = 4
    traces = []
    for arg in args:
        traces.append(go.Scatter(x=df.index,
                                 y=df[products_dct[arg]],
                                 name=arg,
                                 hovertemplate=
                                 'Неделя %{x}' +
                                 '<br>' + '%{y:,} ₽'))
    if len(args) == 1:
        title = f'Продажи {arg} по неделям'
    else:
        title = 'Сравнение продаж нескольких продуктов по неделям'
    layout = go.Layout(title=title,
                       xaxis={'nticks': nticks, 'title': 'Номер недели'},
                       yaxis={'title': 'Продажи, руб', 'rangemode': 'tozero'})

    fig = go.Figure(data=traces, layout=layout)

    return fig


# Body

st.title('Общие метрики по продукту')

st.caption(':red[ВНИМАНИЕ! Данные, представленные на этом сайте, выдуманы и носят  исключительно демонстрационный \
характер. Все совпадения с реальностью случайны.]')

st.header('Период: Январь 2023')

# st.success("Выберите продукт из списка ниже:")
product_of_page = st.selectbox('Выберите продукт из списка ниже:', products_lst)
col_name_of_page_product = products_dct[product_of_page]

st.header(f"Продукт: {product_of_page}")

# Metrics

col11, col12, col13 = st.columns(3)
col11.metric('Продажи, шт', \
             '{0:,}'.format(int(met_df.loc['pieces', col_name_of_page_product])).replace(',', ' '), \
             '{0:,}'.format(int(delta_met_df.loc['pieces', col_name_of_page_product])).replace(',', ' '))
col12.metric('Продажи, руб', \
             '{0:,}'.format(met_df.loc['rub', col_name_of_page_product]).replace(',', ' '), \
             '{0:,}'.format(delta_met_df.loc['rub', col_name_of_page_product]).replace(',', ' '))
col13.metric('Продажи, л', \
             '{0:,}'.format(round(met_df.loc['volume', col_name_of_page_product], 1)).replace(',', ' '), \
             '{0:,}'.format(delta_met_df.loc['volume', col_name_of_page_product]).replace(',', ' '))

# Pie Charts

st.subheader('Доля продукта в категории:')

cats_col_name = ''
if product_of_page == 'Arctic':
    now_cats = cats_dct_for_water
    cat = st.selectbox('Выберите категорию:', now_cats.keys())
    cats_col_name = now_cats[cat]
else:
    now_cats = cats_dct_for_carbonated
    cat = st.selectbox('Выберите категорию:', now_cats.keys())
    cats_col_name = now_cats[cat]

st.plotly_chart(three_plots(met_df))

# Line charts

st.subheader('Продажи по неделям (руб)')

col21, col22 = st.columns(2)

with col21:
    second_products_lst = products_lst.copy()
    second_products_lst.remove(product_of_page)
    second_products_lst.insert(0, 'Нет')
    second_product = st.selectbox('Выберите второй продукт (если необходимо):', second_products_lst)

with col22:
    third_products_lst = second_products_lst.copy()
    third_products_lst.remove(second_product)
    if 'Нет' not in third_products_lst:
        third_products_lst.insert(0, 'Нет')
    disable = False
    if second_product == 'Нет':
        disable = True
    third_products = st.selectbox('Выберите третий продукт (если необходимо):', third_products_lst, disabled=disable)

incomplete_weeks = st.checkbox('Отобразить неполные недели')

if second_product == 'Нет':
    st.plotly_chart(many_products_scatter_line(incomplete_weeks, product_of_page))
else:
    if third_products == 'Нет':
        st.plotly_chart(many_products_scatter_line(incomplete_weeks, product_of_page, second_product))
    else:
        st.plotly_chart(many_products_scatter_line(incomplete_weeks, product_of_page, second_product, third_products))

if incomplete_weeks:
    st.caption('Номер недели "0" отображает данные за 52 неделю согласно стандарту ISO 8601\
     (неделя, включающая только 1 января 2023 года).')
