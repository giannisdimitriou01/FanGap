export function average(values) {
  if (!values.length) {
    return null
  }
  return Math.round((values.reduce((sum, value) => sum + value, 0) / values.length) * 100) / 100
}

export function buildScoreSeries(points) {
  const byDay = new Map()

  for (const point of points) {
    const date = String(point.fetched_at).slice(0, 10)
    let row = byDay.get(date)
    if (!row) {
      row = { date, criticScores: [], fanScores: [] }
      byDay.set(date, row)
    }
    const score = Number(point.score)
    if (Number.isNaN(score)) {
      continue
    }
    if (point.audience === 'critic') {
      row.criticScores.push(score)
    }
    if (point.audience === 'fan') {
      row.fanScores.push(score)
    }
  }

  return [...byDay.values()]
    .sort((left, right) => left.date.localeCompare(right.date))
    .map((row) => {
      const critic = average(row.criticScores)
      const fan = average(row.fanScores)
      return {
        date: row.date,
        critic,
        fan,
        gap:
          critic == null || fan == null
            ? null
            : Math.round(Math.abs(critic - fan) * 100) / 100,
      }
    })
}
