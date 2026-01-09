from typing import Dict, List

from sqlalchemy import case, desc, func, select

from db.session import AsyncSessionLocal
from models.user import Statistic


async def get_last_7_days_stats(telegram_id: int) -> List[Dict]:
    async with AsyncSessionLocal() as session:
        dates_subq = (
            select(Statistic.date)
            .where(Statistic.telegram_id == telegram_id)
            .group_by(Statistic.date)
            .order_by(desc(Statistic.date))
            .limit(7)
            .subquery()
        )

        result = await session.execute(
            select(
                Statistic.date,
                func.coalesce(
                    func.sum(
                        case(
                            (Statistic.action == "water", Statistic.amount),
                            else_=0,
                        )
                    ),
                    0,
                ).label("water_ml"),
                func.coalesce(
                    func.sum(
                        case(
                            (Statistic.action == "food", Statistic.amount),
                            else_=0,
                        )
                    ),
                    0,
                ).label("kcal"),
            )
            .where(
                Statistic.telegram_id == telegram_id,
                Statistic.date.in_(select(dates_subq.c.date)),
            )
            .group_by(Statistic.date)
            .order_by(desc(Statistic.date))
        )

        rows = result.all()
    return [
        {"date": row.date, "water_ml": row.water_ml, "kcal": row.kcal}
        for row in rows
    ]
