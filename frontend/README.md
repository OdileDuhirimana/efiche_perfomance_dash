# Analytics Dashboard Frontend

Next.js frontend application for the analytics dashboard. This is a modern, responsive web application built with React, TypeScript, and Tailwind CSS that displays team performance metrics and analytics.

## What This Frontend Does

The frontend:
- Displays interactive charts and visualizations of team performance data
- Provides filtering capabilities (date range, assignee, issue type)
- Shows executive summary KPIs
- Renders multiple dashboard sections with different metrics
- Connects to the backend API to fetch and display data

## Prerequisites

- **Node.js 18 or higher**
- **npm** (comes with Node.js) or **yarn**
- **Backend API running** on `http://localhost:8050` (or configured URL)

## Quick Start

### Step 1: Install Dependencies

Make sure you're in the `frontend/` directory, then install all required packages:

```bash
npm install
```

This will install all dependencies listed in `package.json`, including:
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS
- Recharts (for charts)

### Step 2: Configure Backend URL

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8050
```

**Important:** 
- The variable name must start with `NEXT_PUBLIC_` to be accessible in the browser
- If your backend runs on a different port or URL, update this accordingly
- Never commit `.env.local` to version control

### Step 3: Start Development Server

```bash
npm run dev
```

The application will start on `http://localhost:3000`

Open your browser and navigate to `http://localhost:3000` to view the dashboard.

## Project Structure

```
frontend/
├── app/
│   ├── components/              # Reusable UI components
│   │   ├── kpi-card.tsx        # KPI display card
│   │   ├── filters.tsx         # Filter controls
│   │   ├── modal.tsx           # Modal dialog component
│   │   ├── sidebar.tsx         # Navigation sidebar
│   │   ├── section-header.tsx  # Section header component
│   │   └── [chart components]  # Various chart components
│   ├── sections/               # Dashboard sections (main content)
│   │   ├── executive-summary.tsx
│   │   ├── throughput-predictability.tsx
│   │   ├── ownership-distribution.tsx
│   │   ├── quality-rework.tsx
│   │   └── company-level.tsx
│   ├── contexts/               # React contexts for state management
│   │   └── FilterContext.tsx   # Global filter state
│   ├── constants/              # Constants and configuration
│   │   └── navigation.tsx     # Navigation menu items
│   ├── types/                  # TypeScript type definitions
│   │   └── navigation.ts
│   ├── layout.tsx              # Root layout component
│   ├── page.tsx                # Main dashboard page
│   └── globals.css             # Global styles
├── lib/
│   ├── api-client.ts           # Backend API client (HTTP requests)
│   └── hooks/                  # Custom React hooks
│       └── use-dashboard-data.ts  # Hooks for fetching dashboard data
├── public/                     # Static assets (images, etc.)
├── package.json                # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── tailwind.config.ts          # Tailwind CSS configuration
└── next.config.ts              # Next.js configuration
```

## Features

### Dashboard Sections

The dashboard is organized into five main sections:

1. **Executive Summary**
   - High-level KPIs: completion rate, average lead time, rework ratio
   - KPI cards show green color when targets are met
   - Planned vs done metrics
   - Quick overview of team performance

2. **Throughput & Predictability**
   - Weekly planned vs done chart
   - Weekly flow analysis (done, in progress, carry over)
   - Lead time trends

3. **Ownership & Distribution**
   - Task load per assignee
   - Execution success rates by assignee
   - Work distribution visualization

4. **Quality & Rework**
   - QA vs Failed QA analysis (grouped by week)
   - Rework ratio tracking
   - Quality metrics over time

5. **Company-Level Trend**
   - Monthly completion rate trends
   - Monthly lead time trends
   - Long-term performance analysis

### Filters

The dashboard includes global filters that apply to all charts:

- **Date Range Filter**: Select a custom date range to analyze
- **Assignee Filter**: Filter data by specific team members
- **Issue Type Filter**: Filter by issue types (Task, Bug, Story, etc.)

All filters are synchronized across all dashboard sections. When you change a filter, all charts update automatically.

## API Integration

The frontend connects to the Flask backend API through the API client located in `lib/api-client.ts`.

### API Client

The `api-client.ts` file handles all HTTP requests to the backend. It:
- Manages API base URL from environment variables
- Handles request/response formatting
- Provides error handling

### Custom Hooks

The application uses custom React hooks for data fetching (located in `lib/hooks/use-dashboard-data.ts`):

| Hook | Description | Parameters |
|------|-------------|------------|
| `useExecutiveSummary()` | Fetches executive KPIs | None |
| `useThroughputData(weeks)` | Fetches weekly planned vs done and flow data | `weeks: number` |
| `useOwnershipData()` | Fetches task load and execution success data | None |
| `useCompanyTrend(months)` | Fetches company-level trend data | `months: number` |
| `useQualityReworkData()` | Fetches quality and rework metrics | None |

All hooks automatically apply the current filter settings from `FilterContext`.

### Example: Using a Hook

```typescript
import { useExecutiveSummary } from '@/lib/hooks/use-dashboard-data';

function MyComponent() {
  const { data, loading, error } = useExecutiveSummary();
  
  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  
  return <div>{/* Display data */}</div>;
}
```

## Development

### Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server on `http://localhost:3000` |
| `npm run build` | Build the application for production |
| `npm start` | Start production server (run `build` first) |
| `npm run lint` | Run ESLint to check code quality |

### Development Workflow

1. **Start the backend API** (in a separate terminal):
   ```bash
   cd ../backend
   python wsgi_api.py
   ```

2. **Start the frontend** (in this terminal):
   ```bash
   npm run dev
   ```

3. **Make changes** to components - the page will automatically reload (hot reload)

4. **Check the browser console** for any errors or warnings

### Adding New Components

1. Create your component file in `app/components/`
2. Use TypeScript for type safety
3. Follow the existing component patterns
4. Use Tailwind CSS for styling

### Adding New Dashboard Sections

1. Create a new file in `app/sections/`
2. Use the appropriate data hooks to fetch data
3. Add the section to the navigation in `app/constants/navigation.tsx`
4. Import and render the section in `app/page.tsx`

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | Yes | `http://localhost:8050` |

**Important Notes:**
- Environment variables must start with `NEXT_PUBLIC_` to be accessible in the browser
- Create `.env.local` for local development (this file is gitignored)
- For production, set environment variables in your hosting platform

## Technologies Used

- **Next.js 16** - React framework with server-side rendering
- **React 19** - UI library
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Recharts** - Charting library for React

## Troubleshooting

### Common Issues

**Problem: "Cannot connect to API" or network errors**
- **Solution:** Make sure the backend API is running on the URL specified in `NEXT_PUBLIC_API_URL`
- **Check:** Verify the backend is accessible: `curl http://localhost:8050/api/health`
- **Check:** Ensure `.env.local` has the correct `NEXT_PUBLIC_API_URL` value

**Problem: "Module not found" errors**
- **Solution:** Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- **Check:** Make sure you're using Node.js 18 or higher: `node --version`

**Problem: Charts not displaying or showing empty data**
- **Solution:** Check the browser console for errors
- **Check:** Verify the backend is returning data by testing the API endpoints directly
- **Check:** Ensure your date range filters aren't excluding all data

**Problem: "Port 3000 already in use"**
- **Solution:** Either stop the process using port 3000, or run on a different port:
  ```bash
  npm run dev -- -p 3001
  ```

**Problem: Build errors or TypeScript errors**
- **Solution:** Run the linter to see specific issues: `npm run lint`
- **Check:** Make sure all TypeScript types are correctly defined
- **Check:** Verify all imports are correct

### Debugging Tips

1. **Check browser console:** Open Developer Tools (F12) and look at the Console tab for errors

2. **Check network requests:** In Developer Tools, go to the Network tab to see API requests and responses

3. **Verify environment variables:** Make sure `.env.local` exists and has the correct values

4. **Test API directly:** Use `curl` or Postman to test if the backend is working:
   ```bash
   curl http://localhost:8050/api/health
   ```

5. **Clear Next.js cache:** If you're seeing strange behavior, try:
   ```bash
   rm -rf .next
   npm run dev
   ```

## Production Build

### Building for Production

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Start the production server:**
   ```bash
   npm start
   ```

The production build is optimized and minified for better performance.

### Deployment Considerations

- Set `NEXT_PUBLIC_API_URL` to your production backend URL
- Ensure your hosting platform supports Node.js
- Consider using a CDN for static assets
- Set up proper error monitoring and logging
- Configure CORS on the backend if deploying to a different domain

## Code Style

- Use TypeScript for all new code
- Follow React best practices (functional components, hooks)
- Use Tailwind CSS utility classes for styling
- Keep components small and focused
- Use meaningful variable and function names
