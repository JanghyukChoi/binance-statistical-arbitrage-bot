from pykalman import KalmanFilter
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint

def kalman_filter_hedge_ratio(y, x):
    """
    Kalman Filter를 사용하여 시간 가변적인 헤지 비율 β(t)를 추정
    """
    delta = 1e-5  # 상태 전이 잡음 (작게 설정)
    trans_cov = delta / (1 - delta) * np.eye(2)  # 상태 전이 공분산
    obs_mat = np.expand_dims(np.vstack([x, np.ones(len(x))]).T, axis=1)

    kf = KalmanFilter(
        transition_matrices=np.eye(2),
        observation_matrices=obs_mat,
        initial_state_mean=np.zeros(2),
        initial_state_covariance=np.ones((2, 2)),
        transition_covariance=trans_cov,
        observation_covariance=1.0
    )

    state_means, _ = kf.filter(y.values)
    hedge_ratios = state_means[:, 0]  # β(t)
    intercepts = state_means[:, 1]    # α(t)
    return hedge_ratios, intercepts

def calculate_cointegration(series1, series2):
    series1, series2 = series1.align(series2, join='inner')
    series1 = series1.dropna()
    series2 = series2.dropna()

    # 공적분 검정
    coint_result = coint(series1, series2)
    t_stat = coint_result[0]
    p_value = coint_result[1]
    critical_value = coint_result[2][1]  # 5% 임계값

    # Kalman Filter로 시간 가변적인 β(t) 추정
    hedge_ratios, intercepts = kalman_filter_hedge_ratio(series1, series2)

    # 시계열별 spread 계산: spread(t) = y(t) - β(t) * x(t) - α(t)
    spread = series1.values - hedge_ratios * series2.values - intercepts

    # Z-score 계산
    zscore = (spread - spread.mean()) / spread.std()

    # 0선 교차 횟수
    zero_crossings = len(np.where(np.diff(np.sign(spread)))[0])

    return {
        'cointegration_flag': int(p_value < 0.05 and t_stat < critical_value),
        'p_value': round(p_value, 4),
        't_value': round(t_stat, 4),
        'critical_value': round(critical_value, 4),
        'hedge_ratio': round(np.mean(hedge_ratios), 4),
        'zero_crossings': zero_crossings,
        'latest_zscore': round(zscore[-1], 4)
    }
