import { buildScoreSeries } from './scoreSeries.js'

describe('buildScoreSeries', () => {
  it('averages critic and fan scores by day', () => {
    const series = buildScoreSeries([
      { fetched_at: '2024-01-01T00:00:00Z', audience: 'critic', score: 80 },
      { fetched_at: '2024-01-01T12:00:00Z', audience: 'critic', score: 90 },
      { fetched_at: '2024-01-01T00:00:00Z', audience: 'fan', score: 70 },
      { fetched_at: '2024-02-01T00:00:00Z', audience: 'fan', score: 72 },
    ])

    expect(series).toEqual([
      { date: '2024-01-01', critic: 85, fan: 70, gap: 15 },
      { date: '2024-02-01', critic: null, fan: 72, gap: null },
    ])
  })

  it('returns an empty series when there are no points', () => {
    expect(buildScoreSeries([])).toEqual([])
  })
})
