import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('Agency Workforce shell', () => {
  it('labels the foundation preview and avoids fake zero metrics', () => {
    render(<App />);
    expect(screen.getByText('Foundation preview')).toBeTruthy();
    expect(screen.getByText(/not zero values/i)).toBeTruthy();
  });
});
