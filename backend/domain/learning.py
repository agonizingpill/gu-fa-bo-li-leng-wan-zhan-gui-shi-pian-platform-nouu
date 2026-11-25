import numpy as np
from sklearn.linear_model import Lasso
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

FEATURE_KEYS = ('heat', 'thick', 'target')
FEATURE_NAMES = ('温度', '片厚', '目标弯度')

def features(row):
    return [row[key] for key in FEATURE_KEYS]

def calculate(data):
    archive = sorted(data['history'], key=lambda row: row['heat'])
    holdout = [row for index, row in enumerate(archive) if index % 4 == 0]
    train = [row for index, row in enumerate(archive) if index % 4 != 0]
    poly = PolynomialFeatures(degree=2, include_bias=False)
    scaler = StandardScaler()
    model = make_pipeline(poly, scaler,
                          Lasso(alpha=data['penalty'], max_iter=20000))
    model.fit([features(row) for row in train], [row['measured'] for row in train])
    errors = model.predict([features(row) for row in holdout]) - [row['measured'] for row in holdout]
    terms = poly.get_feature_names_out(list(FEATURE_NAMES))
    lasso = model[-1]
    # 完整管线参数随计算结果返回，签注时固化进曲线，之后倒查不再依赖本次计算记录
    fitted = {'feature_names': list(terms),
              'scaler_mean': [float(v) for v in scaler.mean_],
              'scaler_scale': [float(v) for v in scaler.scale_],
              'coef': [float(v) for v in lasso.coef_],
              'intercept': float(lasso.intercept_),
              'train_heat_min': min(row['heat'] for row in train),
              'train_heat_max': max(row['heat'] for row in train),
              'usual_heat': float(np.mean([row['heat'] for row in train]))}
    return {'prediction': round(float(model.predict([features(data['coupon'])])[0]), 3),
            'mae': round(float(np.mean(np.abs(errors))), 3), 'held_out': len(holdout),
            'terms': [term for term, coef in zip(terms, lasso.coef_) if abs(coef) > 1e-10],
            'fitted': fitted}
