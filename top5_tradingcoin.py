import pandas as pd
import numpy as np

df = pd.read_csv("cointegrated_pairs.csv")


# 이상치 필터링
df = df[df['hedge_ratio'].abs() < 10000]

# 점수화
df['score_p'] = 1 - df['p_value']
df['score_z'] = np.abs(df['latest_zscore'])
df['score_cross'] = df['zero_crossings']
df['score_hedge'] = -np.log1p(np.abs(df['hedge_ratio']))
df['score_t'] = -df['t_value']

# 정규화
for col in ['score_p', 'score_z', 'score_cross', 'score_hedge', 'score_t']:
    df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

# 수학적으로 최적의 가중치: PCA 기반 첫 번째 주성분을 가중치로 사용
from sklearn.decomposition import PCA

scores_matrix = df[['score_p', 'score_z', 'score_cross', 'score_hedge', 'score_t']]
pca = PCA(n_components=1)
pca.fit(scores_matrix)
optimal_weights = pca.components_[0]
optimal_weights = optimal_weights / optimal_weights.sum()  # 합이 1이 되도록 정규화

# 최종 점수 계산
df['final_score'] = scores_matrix.dot(optimal_weights)

# 상위 5개 쌍 추출
top5 = df.sort_values(by='final_score', ascending=False).head(5)

# 저장
top5.to_csv("top5_cointegrated_pairs.csv", index=False)

# 결과 출력
print("통계적 차익거래에 최적의 상위 5개 쌍:")
print(top5[['symbol_1', 'symbol_2', 'final_score', 'p_value', 'latest_zscore', 'zero_crossings']])