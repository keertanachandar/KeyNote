# KeyNote React/TypeScript Frontend Mockup

## Visual Layout

### Header
```
┌─────────────────────────────────────────────────────────────┐
│  🎸 KeyNote                                                  │
│  AI-Powered Chord Progression Assistant for Songwriters     │
└─────────────────────────────────────────────────────────────┘
```

### Main Content Area

```
┌─────────────────────────────────────────────────────────────┐
│                                                               │
│  📝 Describe Your Song                                       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Song Description                                     │    │
│  │ e.g., melancholic indie folk, slow tempo            │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Song Lyrics (Optional)                              │    │
│  │                                                      │    │
│  │ Verse 1:                                            │    │
│  │ ...                                                 │    │
│  │                                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────────┐  ┌─────────────────────────────────┐     │
│  │ Preferred    │  │ Reference Artists (Optional)     │     │
│  │ Key: C ▼     │  │ e.g., Bon Iver, Phoebe Bridgers │     │
│  └──────────────┘  └─────────────────────────────────┘     │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │      🎵 Generate Chord Progressions                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Results Section (After Generation)

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Lyrics Analysis                                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Mood: Melancholic  │ Genre: Indie Folk  │ Energy: Low │  │
│  │ Emotional Arc: Grief to acceptance                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  🎵 Your Chord Progression Options                           │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  🎹 Player Settings (applies to all progressions)     │  │
│  │                                                         │  │
│  │  Instrument: [Piano ▼]    Tempo: [━━●━━━━━] 120 BPM  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  [Option 1 (85%)] [Option 2 (78%)] [Option 3] [Option 4]   │
│  ─────────────────────────────────────────────────────────   │
│                                                               │
│  🎯 I - V - vi - IV                                          │
│  85% Excellent Match                                         │
│                                                               │
│  Chords in C: C - G - Am - F                                │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  🎹 Listen to This Progression                         │  │
│  │                                                         │  │
│  │  [C]  [G]  [Am]  [F]  ← Click to select              │  │
│  │                                                         │  │
│  │  [▶ Play]  [▶ Play Selected]  [🔁 Loop]  [⏹ Stop]   │  │
│  │                                                         │  │
│  │  💡 Click chords to select • Your settings are saved  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  📖 About This Progression                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ Frequency: Very Common                                 │  │
│  │ Genres: Pop, Rock, Indie                              │  │
│  │ Example Songs: "Let It Be", "Don't Stop Believin'"   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
│  🎓 Music Theory for This Progression                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ [Show Theory Explanation] ▼                           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Design Features

### Modern UI Components (shadcn/ui + Tailwind)

1. **Clean, Professional Look**
   - White/slate color scheme
   - Subtle shadows and borders
   - Smooth animations
   - Responsive design

2. **Interactive Elements**
   - Hover effects on buttons
   - Smooth transitions
   - Loading states with spinners
   - Toast notifications for errors

3. **Typography**
   - Clean, readable fonts
   - Proper heading hierarchy
   - Good spacing and contrast

### Color Scheme

```
Primary: Indigo/Blue (#667eea)
Background: Slate-50 to Slate-100 gradient
Cards: White with subtle shadow
Text: Slate-900 (dark) / Slate-600 (secondary)
Accent: Green (for success), Red (for errors)
```

### Responsive Design

**Desktop (>1024px)**
```
┌─────────────────────────────────────────┐
│  Header                                  │
├─────────────┬───────────────────────────┤
│             │                           │
│  Input Form │  (Reserved for future)   │
│             │                           │
├─────────────┴───────────────────────────┤
│  Full-width Results                     │
└─────────────────────────────────────────┘
```

**Tablet (768px - 1024px)**
```
┌───────────────────────┐
│  Header               │
├───────────────────────┤
│  Input Form           │
│  (Full width)         │
├───────────────────────┤
│  Results              │
│  (Full width)         │
└───────────────────────┘
```

**Mobile (<768px)**
```
┌──────────────┐
│  Header      │
├──────────────┤
│  Form        │
│  (Stacked)   │
├──────────────┤
│  Results     │
│  (Stacked)   │
└──────────────┘
```

## Component Breakdown

### 1. SongInputForm.tsx
```tsx
- Description input (text)
- Lyrics textarea (multiline)
- Reference artists input (text)
- Preferred key selector (dropdown)
- Vocal range selector (dropdown)
- Generate button (large, primary)
- Loading state (spinner + "Generating...")
```

### 2. ProgressionResults.tsx
```tsx
- Lyrics analysis card (collapsible)
- Player settings bar (instrument + tempo)
- Progression tabs (clickable)
- Match scores (badges)
```

### 3. ProgressionCard.tsx
```tsx
- Roman numeral notation (large heading)
- Match score badge
- Current key chords (with transposition info)
- Chord player component
- Progression metadata (genres, frequency, examples)
- Music theory section (collapsible)
```

### 4. ChordPlayer.tsx
```tsx
- Chord buttons (clickable to select)
- Play controls (Play, Play Selected, Loop, Stop)
- Visual feedback (selected chords highlighted)
- Auto-stop on tab switch
- Tone.js integration
```

### 5. LyricsAnalysis.tsx
```tsx
- Overall stats grid (mood, genre, energy)
- Emotional arc display
- Song structure breakdown
- Emotional peaks list
- Section-specific recommendations
- Collapsible sections
```

## Comparison: Streamlit vs React

### Current Streamlit
```
✅ Works now
✅ All features implemented
✅ Python-native
❌ Less customizable UI
❌ Can't deploy to Vercel
❌ Streamlit-specific styling
```

### New React/TypeScript
```
✅ Deploy to Vercel
✅ Fully customizable UI
✅ Modern, professional look
✅ Better performance
✅ Industry-standard tech stack
❌ Requires building frontend
❌ More setup time
❌ Need to recreate all components
```

## Interactive Features

### 1. Form Validation
```
- Required field indicators
- Real-time validation messages
- Disabled submit until valid
```

### 2. Loading States
```
- Skeleton loaders while generating
- Progress indicators
- Smooth transitions
```

### 3. Error Handling
```
- Toast notifications for errors
- Retry buttons
- Clear error messages
```

### 4. Animations
```
- Fade in results
- Smooth tab transitions
- Button hover effects
- Chord selection animations
```

## Technologies Used

### Frontend Stack
```
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Tone.js (audio)
- React Query (API calls)
- Axios (HTTP client)
```

### Why These?
- **Next.js**: Best React framework, Vercel-optimized
- **TypeScript**: Type safety, better DX
- **Tailwind**: Rapid styling, customizable
- **shadcn/ui**: Beautiful, accessible components
- **React Query**: Smart data fetching, caching
- **Tone.js**: Same audio library you're using now

## Performance

### Optimizations
```
- Server-side rendering (SSR) for initial load
- Client-side routing (instant page transitions)
- Lazy loading components
- Image optimization (Next.js built-in)
- API response caching
- Debounced inputs
```

### Load Times
```
- Initial load: 1-2s (with SSR)
- Subsequent navigations: <100ms (client-side)
- API calls: Same as now (depends on backend)
```

## Accessibility

```
- Keyboard navigation
- Screen reader support
- ARIA labels
- Focus management
- High contrast mode support
- Semantic HTML
```

---

## Summary

The React frontend will look **very similar** to your current Streamlit app, but with:

✨ **More polished** - Professional UI components
🚀 **Better performance** - Optimized loading and routing
🎨 **Fully customizable** - Control every pixel
📱 **Fully responsive** - Perfect on mobile, tablet, desktop
🔧 **Type-safe** - TypeScript catches errors early
☁️ **Vercel-ready** - Deploy with one command

**Same features, better presentation!**

