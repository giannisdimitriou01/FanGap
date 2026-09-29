import { render, screen } from '@testing-library/react'
import { expect, it } from 'vitest'

import ScoreChart from './ScoreChart.jsx'

it('shows an empty state when there is no history', () => {
  render(<ScoreChart points={[]} />)
  expect(screen.getByText(/No rating history yet/)).toBeInTheDocument()
})
