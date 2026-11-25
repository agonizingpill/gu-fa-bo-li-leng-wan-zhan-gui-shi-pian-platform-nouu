"""按签注时固化的曲线，由片厚、工艺目标和成品弯度反查炉温。

曲线模型为 PolynomialFeatures(degree=2) + StandardScaler + Lasso。
固定片厚与目标弯度后，预测弯度关于炉温是二次函数，可直接求解析根；
只接受落在训练温区 [train_heat_min, train_heat_max] 内的根。
"""

import math

# learning.calculate 固化的 fitted 结构里必须齐备的字段
FITTED_FIELDS = ('feature_names', 'scaler_mean', 'scaler_scale', 'coef',
                 'intercept', 'train_heat_min', 'train_heat_max', 'usual_heat')
POLY_TERMS = 9
# PolynomialFeatures(degree=2, include_bias=False) 的特征顺序
POLY_POWERS = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (2, 0, 0), (1, 1, 0),
               (1, 0, 1), (0, 2, 0), (0, 1, 1), (0, 0, 2))


def curve_complete(curve):
    """缺参数的老曲线只供查阅，不能参与倒查。"""
    if not isinstance(curve, dict) or 'fitted' not in curve:
        return False
    fitted = curve['fitted']
    if not isinstance(fitted, dict) or any(key not in fitted for key in FITTED_FIELDS):
        return False
    return len(fitted['feature_names']) == POLY_TERMS and len(fitted['coef']) == POLY_TERMS \
        and len(fitted['scaler_mean']) == POLY_TERMS and len(fitted['scaler_scale']) == POLY_TERMS \
        and all(value > 0 for value in fitted['scaler_scale']) \
        and fitted['train_heat_min'] <= fitted['train_heat_max']


def _scaled_poly(heat, thick, target, fitted):
    raw = (heat, thick, target)
    poly = [raw[0] ** p0 * raw[1] ** p1 * raw[2] ** p2 for p0, p1, p2 in POLY_POWERS]
    return [(poly[i] - fitted['scaler_mean'][i]) / fitted['scaler_scale'][i]
            for i in range(POLY_TERMS)]


def predict(curve, heat, thick, target):
    """用签注曲线在给定炉温、片厚、工艺目标下预测冷却弯度。"""
    fitted = curve['fitted']
    scaled = _scaled_poly(heat, thick, target, fitted)
    return fitted['intercept'] + sum(c * z for c, z in zip(fitted['coef'], scaled))


def _raw_quadratic(fitted, thick, target):
    """把标准化空间的 Lasso 线性式展开回原始特征空间。

    每个标准化特征为 (raw_i - mean_i) / scale_i，其中
    raw_i = heat^p0 * thick^p1 * target^p2。固定片厚与目标后，
    汇总得到预测弯度关于炉温的 quad*heat^2 + linear*heat + constant。
    """
    quad = linear = 0.0
    constant = fitted['intercept']
    t, g = thick, target
    for i, (p0, p1, p2) in enumerate(POLY_POWERS):
        weight = fitted['coef'][i] / fitted['scaler_scale'][i]
        mean = fitted['scaler_mean'][i]
        tail = t ** p1 * g ** p2
        if p0 == 0:
            constant += weight * (tail - mean)
        elif p0 == 1:
            linear += weight * tail
            constant -= weight * mean
        else:
            quad += weight * tail
            constant -= weight * mean
    return quad, linear, constant


def lookup_heat(curve, thick, target, measured):
    """返回 {'heat': 炉温或 None, 'candidates': [...], 'reason': 无解说明}。"""
    fitted = curve['fitted']
    quad, linear, constant = _raw_quadratic(fitted, thick, target)
    # 预测弯度 = quad*heat^2 + linear*heat + constant，反解 measured
    roots = []
    eps = 1e-12
    if abs(quad) < eps:
        if abs(linear) >= eps:
            roots = [(measured - constant) / linear]
        elif abs(constant - measured) < 1e-9:
            roots = [fitted['usual_heat']]  # 恒等命中：任何炉温均可，取常用炉温
    else:
        discriminant = linear * linear - 4 * quad * (constant - measured)
        tolerance = 1e-9 * max(1.0, linear * linear, abs(4 * quad * (constant - measured)))
        if discriminant < -tolerance:
            return _no_solution(fitted, '曲线在训练温区内无法达到该成品弯度')
        discriminant = max(discriminant, 0.0)
        root = math.sqrt(discriminant)
        roots = [(-linear - root) / (2 * quad), (-linear + root) / (2 * quad)] \
            if root > eps else [-linear / (2 * quad)]

    low, high = fitted['train_heat_min'], fitted['train_heat_max']
    candidates = sorted({round(heat, 2) for heat in roots
                         if low - 1e-9 <= heat <= high + 1e-9})
    if not candidates:
        return _no_solution(fitted, '方程有解但炉根落在训练温区之外')
    usual = fitted['usual_heat']
    # 多解挑离常用炉温最近的；等距时取较低炉温，保证结果可复现
    chosen = min(candidates, key=lambda heat: (abs(heat - usual), heat))
    return {'heat': chosen, 'candidates': candidates, 'reason': None,
            'usual_heat': usual, 'train_heat_min': low, 'train_heat_max': high}


def _no_solution(fitted, reason):
    return {'heat': None, 'candidates': [], 'reason': reason,
            'usual_heat': fitted['usual_heat'],
            'train_heat_min': fitted['train_heat_min'],
            'train_heat_max': fitted['train_heat_max']}
