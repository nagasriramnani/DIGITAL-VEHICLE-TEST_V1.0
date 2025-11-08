# 🚀 React/Next.js Migration Guide

**Complete guide for migrating from Streamlit to a modern React/Next.js frontend**

---

## Overview

This guide provides step-by-step instructions for building a modern React/Next.js frontend that connects to your existing FastAPI backend.

---

## Why Migrate?

### Current (Streamlit)
- ✅ Quick to build
- ✅ Python-based
- ⚠️ Limited customization
- ⚠️ Less modern UI
- ⚠️ Framework constraints

### Future (React/Next.js)
- ✅ Complete design freedom
- ✅ Modern UI libraries (shadcn/ui)
- ✅ Better performance
- ✅ Professional appearance
- ✅ Mobile responsive
- ✅ Better animations/UX

---

## Tech Stack Recommendation

### Frontend Framework
- **Next.js 14** (App Router) - Latest React framework
- **React 18** - UI library
- **TypeScript** - Type safety

### UI Libraries
- **shadcn/ui** - Beautiful, accessible components
- **Tailwind CSS** - Utility-first CSS
- **Framer Motion** - Smooth animations
- **Recharts** - Modern charting library

### State Management
- **Zustand** - Lightweight state management
- **React Query** - Server state management
- **Axios** - HTTP client

---

## Step 1: Project Setup

### 1.1 Create Next.js Project

```bash
# Create Next.js app with TypeScript and Tailwind
npx create-next-app@latest vta-frontend \
  --typescript \
  --tailwind \
  --app \
  --no-src-dir \
  --import-alias "@/*"

cd vta-frontend
```

### 1.2 Install Dependencies

```bash
# UI Components
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input select label badge table

# Charts
npm install recharts

# HTTP Client
npm install axios

# State Management
npm install zustand @tanstack/react-query

# Animations
npm install framer-motion

# Icons
npm install lucide-react

# Utilities
npm install clsx tailwind-merge
```

### 1.3 Project Structure

```
vta-frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx             # Dashboard (home)
│   ├── recommendations/
│   │   └── page.tsx
│   ├── roi/
│   │   └── page.tsx
│   ├── metrics/
│   │   └── page.tsx
│   ├── governance/
│   │   └── page.tsx
│   ├── simulation/
│   │   └── page.tsx
│   └── scenarios/
│       └── page.tsx
├── components/
│   ├── ui/                  # shadcn components
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── Navigation.tsx
│   ├── dashboard/
│   │   ├── MetricCard.tsx
│   │   ├── ChartCard.tsx
│   │   └── StatsOverview.tsx
│   ├── recommendations/
│   │   ├── RecommendationForm.tsx
│   │   └── RecommendationList.tsx
│   └── charts/
│       ├── PieChart.tsx
│       ├── BarChart.tsx
│       └── LineChart.tsx
├── lib/
│   ├── api.ts               # API client
│   ├── utils.ts             # Utilities
│   └── types.ts              # TypeScript types
├── hooks/
│   ├── useRecommendations.ts
│   ├── useROI.ts
│   └── useMetrics.ts
└── styles/
    └── globals.css
```

---

## Step 2: API Integration

### 2.1 Create API Client

**`lib/api.ts`:**

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const apiEndpoints = {
  health: () => api.get('/health'),
  recommendations: (data: RecommendationRequest) => 
    api.post('/api/v1/recommendations', data),
  roi: (data: ROIRequest) => 
    api.post('/api/v1/roi', data),
  metrics: (data: MetricsRequest) => 
    api.post('/api/v1/metrics', data),
  scenarios: (params?: { limit?: number; offset?: number }) => 
    api.get('/api/v1/scenarios', { params }),
  governance: {
    status: () => api.get('/api/v1/governance/status'),
    lmcReport: (quarter: string) => 
      api.post('/api/v1/governance/lmc-report', null, { params: { quarter } }),
  },
  simulation: {
    export: (data: SimulationExportRequest) => 
      api.post('/api/v1/simulation/export', data),
  },
};
```

### 2.2 TypeScript Types

**`lib/types.ts`:**

```typescript
export interface RecommendationRequest {
  vehicle_model: string;
  platform: 'EV' | 'HEV' | 'ICE';
  systems: string[];
  components: string[];
  top_k: number;
}

export interface Recommendation {
  scenario_id: string;
  test_name: string;
  score: number;
  test_type: string;
  metadata: {
    estimated_cost_gbp: number;
    estimated_duration_hours: number;
    complexity_score?: number;
    risk_level?: string;
  };
  explain: {
    scores: {
      semantic: number;
      graph: number;
      rules: number;
      historical: number;
    };
    rules_fired?: string[];
  };
}

export interface ROIRequest {
  baseline_scenarios: any[];
  optimized_scenarios: any[];
  implementation_cost_gbp: number;
  analysis_period_years: number;
}

export interface MetricsRequest {
  scenarios: any[];
  all_components: string[];
  all_systems: string[];
  all_platforms: string[];
  required_standards: string[];
  num_duplicates: number;
  optimization_rate: number;
}
```

---

## Step 3: Core Components

### 3.1 Layout Components

**`components/layout/Sidebar.tsx`:**

```typescript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Target, 
  DollarSign, 
  BarChart3, 
  Building2, 
  Rocket, 
  FileText 
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/recommendations', label: 'Recommendations', icon: Target },
  { href: '/roi', label: 'ROI Analysis', icon: DollarSign },
  { href: '/metrics', label: 'Metrics', icon: BarChart3 },
  { href: '/governance', label: 'Governance', icon: Building2 },
  { href: '/simulation', label: 'Simulation', icon: Rocket },
  { href: '/scenarios', label: 'Scenarios', icon: FileText },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-white/95 backdrop-blur-lg border-r border-blue-100 shadow-lg">
      <div className="p-6">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-cyan-500 bg-clip-text text-transparent">
          🚗 VTA
        </h1>
      </div>
      <nav className="px-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all",
                isActive
                  ? "bg-gradient-to-r from-blue-50 to-cyan-50 text-blue-600 font-semibold border-l-4 border-blue-600"
                  : "text-gray-600 hover:bg-gray-50 hover:text-blue-600"
              )}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
```

### 3.2 Metric Card Component

**`components/dashboard/MetricCard.tsx`:**

```typescript
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  delta?: number;
  icon?: React.ReactNode;
  className?: string;
}

export function MetricCard({ title, value, delta, icon, className }: MetricCardProps) {
  return (
    <Card className={cn("hover:shadow-xl transition-all duration-300 hover:-translate-y-1", className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-gray-600 uppercase tracking-wide">
          {title}
        </CardTitle>
        {icon && <div className="text-blue-600">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-3xl font-bold text-blue-600">{value}</div>
        {delta !== undefined && (
          <div className={cn(
            "flex items-center gap-1 text-xs mt-2",
            delta >= 0 ? "text-green-600" : "text-red-600"
          )}>
            {delta >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
            <span>{Math.abs(delta)}%</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## Step 4: Pages Implementation

### 4.1 Dashboard Page

**`app/page.tsx`:**

```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { apiEndpoints } from '@/lib/api';
import { MetricCard } from '@/components/dashboard/MetricCard';
import { ChartCard } from '@/components/dashboard/ChartCard';
import { Activity, DollarSign, Zap, Shield } from 'lucide-react';

export default function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => apiEndpoints.scenarios({ limit: 500 }).then(res => res.data),
  });

  const scenarios = stats?.scenarios || [];
  const totalCost = scenarios.reduce((sum: number, s: any) => sum + (s.estimated_cost_gbp || 0), 0);
  const evScenarios = scenarios.filter((s: any) => s.applicable_platforms?.includes('EV')).length;
  const certScenarios = scenarios.filter((s: any) => s.certification_required).length;

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-cyan-500 to-purple-600 bg-clip-text text-transparent mb-2">
          Virtual Testing Assistant
        </h1>
        <p className="text-gray-600">AI-powered test optimization dashboard</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Scenarios"
          value={scenarios.length}
          icon={<Activity className="w-6 h-6" />}
        />
        <MetricCard
          title="Total Cost"
          value={`£${(totalCost / 1000).toFixed(0)}K`}
          icon={<DollarSign className="w-6 h-6" />}
        />
        <MetricCard
          title="EV Scenarios"
          value={evScenarios}
          icon={<Zap className="w-6 h-6" />}
        />
        <MetricCard
          title="Certification Tests"
          value={certScenarios}
          icon={<Shield className="w-6 h-6" />}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Test Distribution" type="pie" data={scenarios} />
        <ChartCard title="Platform Distribution" type="bar" data={scenarios} />
      </div>
    </div>
  );
}
```

---

## Step 5: Deployment

### 5.1 Environment Variables

**`.env.local`:**

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 5.2 Build & Run

```bash
# Development
npm run dev

# Production build
npm run build
npm start
```

### 5.3 Docker Integration

Add to `docker-compose.yml`:

```yaml
frontend:
  build:
    context: ./vta-frontend
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
  environment:
    NEXT_PUBLIC_API_URL: http://api:8000
  depends_on:
    - api
```

---

## Migration Checklist

- [ ] Set up Next.js project
- [ ] Install dependencies
- [ ] Create API client
- [ ] Build layout components
- [ ] Implement Dashboard page
- [ ] Implement Recommendations page
- [ ] Implement ROI page
- [ ] Implement Metrics page
- [ ] Implement Governance page
- [ ] Implement Simulation page
- [ ] Implement Scenarios page
- [ ] Add charts and visualizations
- [ ] Add loading states
- [ ] Add error handling
- [ ] Test all API integrations
- [ ] Deploy frontend
- [ ] Update CORS in FastAPI

---

## Quick Start Template

I can generate a complete Next.js project structure for you. Would you like me to:

1. **Create the full Next.js project files** (recommended)
2. **Provide enhanced Streamlit version** (faster, keeps current stack)
3. **Both** (enhanced Streamlit now, React later)

Let me know your preference!

