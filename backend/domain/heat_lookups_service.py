from sqlalchemy import select

from core.records import get, insert, need, update
from domain.heat_lookups_model import heat_lookups
from domain.inverse import curve_complete, lookup_heat
from domain.profiles_model import profiles


def _same_parameters(order, data):
    return order['profile'] == data.profile and abs(order['thick'] - data.thick) < 1e-9 \
        and abs(order['target'] - data.target) < 1e-9 \
        and abs(order['measured'] - data.measured) < 1e-9


def create_lookup(conn, user, data):
    profile = get(conn, profiles, data.profile)
    need(1.5 <= data.thick <= 10, '片厚超出试制档范围')
    need(data.target > 0 and data.measured >= 0, '工艺目标或成品弯度不成立')
    need(curve_complete(profile['curve']), '该曲线缺少拟合参数，仅供查阅，不能倒查炉温')
    existing = conn.execute(select(heat_lookups).where(heat_lookups.c.code == data.code)) \
        .mappings().first()
    if existing is not None:
        # 同编号重试直接回单，不新增倒查单；参数被改则拒绝
        existing = dict(existing)
        need(_same_parameters(existing, data), '倒查单编号已用于另一组片厚、目标或弯度')
        return existing
    answer = lookup_heat(profile['curve'], data.thick, data.target, data.measured)
    state = '待确认' if answer['heat'] is not None else '无炉温'
    return insert(conn, heat_lookups, code=data.code, profile=data.profile,
        thick=data.thick, target=data.target, measured=data.measured,
        heat=answer['heat'], candidates=answer['candidates'],
        usual_heat=answer['usual_heat'], state=state, reason=answer['reason'])


def confirm_lookup(conn, user, data):
    order = get(conn, heat_lookups, data.code, lock=True)
    need(order['heat'] is not None, '该倒查单在训练温区内无炉温，不给确认')
    need(order['state'] == '待确认', '倒查单已经确认，以首次确认的炉温和曲线版本为准')
    return update(conn, heat_lookups, data.code, state='已确认')
