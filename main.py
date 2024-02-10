from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import os
from fastapi import HTTPException
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import requests
import httpx

app = FastAPI()

# CSVファイルの読み込み（一度だけ行う）
file_path = "movies_data6.csv"
movies_data = pd.read_csv(file_path)

# ファイルが存在する場合のみ読み込みを行う
if os.path.exists(file_path):
    movies_data = pd.read_csv(file_path)
else:
    print(f"File not found: {file_path}")
class MovieRequest(BaseModel):
    movie_id: int

def get_movie_id_endpoint(category: str, year: int):
    return hash(f"{category}{year}")
    # カテゴリと年代に基づいて映画IDを取得するFastAPIエンドポイント

@app.get("/get_movie_id_endpoint")
async def get_movie_id_endpoint(
    category: str = Query(..., title="映画のカテゴリ"),
    year: int = Query(..., title="映画の年代"),
):
    # 実際の映画IDの取得処理をここで行う（例: hash関数を使用）
    movie_id = get_movie_id_endpoint(category, year)

    # 類似映画を取得するリクエストを送信
    api_url2 = "https://_ _ _ _ _ .onrender.com/get_movie_id_endpoint"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(api_url2, json={"movie_id": movie_id})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # FastAPIサーバーがエラーを返した場合の処理
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except httpx.RequestError as e:
            # リクエスト自体が失敗した場合の処理
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_similar_movies")
def get_similar_movies(request: MovieRequest):
    try:
        movie_id = request.movie_id
        # Sentence BERTを使用して類似映画を計算する処理
        texts = []  # テキストデータを格納するリスト

        nltk.download('punkt')
        nltk.download('stopwords')

        # テキストのクリーニング関数
        def clean_text(text):
            text = text.lower()
            text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
            text = re.sub(r'\d+', '番号', text)
            return text

        # ストップワードの削除関数
        def remove_stopwords(text):
            stop_words = set(stopwords.words('english'))
            tokens = word_tokenize(text)
            filtered_tokens = [word for word in tokens if word not in stop_words]
            return ' '.join(filtered_tokens)
         # Sentence-BERTモデルの読み込み
        
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

        # CSVファイルからテキストを読み込み
        texts = []
        texts.extend(movies_data['reviews'].tolist())  # 'reviews'にはテキストが入っている列の名前を指定してください

        # それぞれのテキストにクリーニングとストップワードの削除を適用
        processed_texts = []
        for text in texts:
            cleaned_text = clean_text(text)
            processed_text = remove_stopwords(cleaned_text)
            processed_texts.append(processed_text)

        # クリーニングされたテキストをSBERTを用いて埋め込みに変換
        embeddings = model.encode(processed_texts)

        # テキスト間の類似度を計算
        similarity_scores = cosine_similarity(embeddings[movie_id].reshape(1, -1), embeddings).flatten()
        similar_movies_indices = similarity_scores.argsort()[-4:-1][::-1]  # 類似度が高い映画のインデックス（自分自身を含むので上位4つ）
        
        # データフレームからタイトルを抽出
        similar_movies = movies_data['items.title'].iloc[similar_movies_indices].tolist()

        return {"similar_movies": similar_movies}
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))