# data/rag_preprocessor.py

import pandas as pd
import re
from typing import Union

def load_csv(file_path: str) -> pd.DataFrame:
    """
    id, title, content 컬럼을 가진 CSV 파일을 불러옵니다.
    """
    df = pd.read_csv(file_path)
    required_columns = {'id', 'title', 'content'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"CSV must contain columns: {required_columns}")
    return df


def clean_text(text: Union[str, float]) -> str:
    """
    텍스트 정제: 줄바꿈, 탭 제거 및 공백 정리
    """
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r'\s+', ' ', text)  # 여러 공백/줄바꿈 → 하나의 공백
    return text.strip()


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    title, content를 정제하고 결합하여 combined 열 생성
    """
    df['title'] = df['title'].apply(clean_text)
    df['content'] = df['content'].apply(clean_text)
    df['combined'] = df['title'] + " " + df['content']
    return df[['id', 'combined']]
