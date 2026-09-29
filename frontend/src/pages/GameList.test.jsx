import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'

import GameList from '../pages/GameList.jsx'

beforeEach(() => {
  vi.stubGlobal(
    'fetch',
    vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({
        items: [
          {
            igdb_id: 113112,
            title: 'Hades',
            release_date: '2020-09-17',
            genres: ['Action'],
            platforms: ['PC'],
            cover_url: null,
          },
        ],
        total: 1,
        page: 1,
        page_size: 20,
      }),
    })),
  )
})

afterEach(() => {
  vi.unstubAllGlobals()
})

it('renders catalog games from IGDB search', async () => {
  render(
    <MemoryRouter>
      <GameList />
    </MemoryRouter>,
  )
  expect(await screen.findByRole('heading', { name: 'Hades' })).toBeInTheDocument()
})
