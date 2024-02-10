import streamlit as st
import requests
import pandas as pd
import os

# Streamlitアプリケーション
st.title("映画おすすめアプリ")
st.balloons()

#CSVファイルの読み込み（一度だけ行う）
file_path = "movies_data6.csv"
movies_data = pd.read_csv(file_path)

# 映画カテゴリの選択肢リスト
movie_categories = movies_data['Category'].unique()

# 映画カテゴリの選択ボックス
selected_movie_category = st.selectbox(
    "好きな映画のカテゴリを選んでください",
    movie_categories,
)
# 映画の年代の選択肢リスト
movie_years = {
    '1930s': (1930, 1939),
    '1940s': (1940, 1949),
    '1950s': (1950, 1959),
    '1960s': (1960, 1969),
    '1970s': (1970, 1979),
    '1980s': (1980, 1989),
    '1990s': (1990, 1999),
    '2000s': (2000, 2009),
    '2010s': (2010, 2019),
    '2020s': (2020, 2024),
}

# 選択された年代を取得
selected_movie_year_str = st.selectbox(
    "好きな映画の年代を選んでください",
    list(movie_years.keys()),
)
# 年代の形式が '1930s' から 1930 に変換されます
selected_movie_year = int(selected_movie_year_str[:-1])

# 選択されたカテゴリと年代から映画IDを抽出
selected_movie_ids = movies_data[
    (movies_data['Category'] == selected_movie_category) &
    (movies_data['items.year'].between(*movie_years[selected_movie_year_str]))
]['movie_id'].tolist()

# 選択された映画IDを表示
st.subheader('お気に入り映画を選択:')
selected_movie_title = st.selectbox(
    "お気に入りの映画を選んでください",
    movies_data[movies_data['movie_id'].isin(selected_movie_ids)]['items.title']
)
# #### FastAPIサーバーのエンドポイント
# api_url2 = "http://localhost:8000/get_movie_id_endpoint"

# # 選択された映画IDが存在する場合
# if selected_movie_ids:
#     # 選択されたカテゴリと年代から映画IDを取得
#     response = requests.get(api_url2, json={"movie_id": selected_movie_ids[0]})

#     # 映画IDから類似映画を取得
#     if response.status_code == 200:
#         try:
#             similar_movies = response.json().get("similar_movies", [])
#             # 結果を表示
#             st.write("類似映画:")
#             for i, movie in enumerate(similar_movies, start=1):
#                 st.write(f"{i}. {movie}")
#         except Exception as e:
#             st.error(f"Error parsing response JSON: {str(e)}")
#     else:
#         st.error(f"Error: {response.status_code} - {response.text}")
# else:
#     st.warning("選択された映画IDがありません。")

# FastAPIサーバーのエンドポイント
api_url = "https://_ _ _ _ _ .onrender.com/get_similar_movies"    

# 選択された映画のIDから類似映画を取得
response = requests.post(api_url, json={"movie_id": selected_movie_ids[0]})

# 類似映画を表示
if response.status_code == 200:
    try:
        similar_movies = response.json().get("similar_movies", [])
        # 結果を表示
        st.write("類似映画:")
        for i, movie in enumerate(similar_movies, start=1):
            st.write(f"{i}. {movie}")
    except Exception as e:
        st.error(f"Error parsing response JSON: {str(e)}")
else:
    st.error(f"Error: {response.status_code} - {response.text}")