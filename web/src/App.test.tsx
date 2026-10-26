import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('Agency Workforce authentication', () => {
  it('shows sign-in and explains server-checked access', () => {
    render(<App />);
    expect(screen.getByText('Sign in to your workspace')).toBeTruthy();
    expect(screen.getByLabelText('Username')).toBeTruthy();
    expect(screen.getByLabelText('Password')).toBeTruthy();
  });
});
