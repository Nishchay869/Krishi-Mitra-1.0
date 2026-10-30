# Shared farm UI

The site uses a forest-green, warm-white and sage palette, outlined surfaces, restrained shadows and generous spacing. `static/css/premium.css` is the shared visual layer over existing Django pages. It also supplies scoped resets for shadcn islands because global Tailwind preflight is intentionally disabled alongside Bootstrap.

Components were discovered and inspected through the configured **shadcn MCP server** using `search_items_in_registries`, `view_items_in_registries` and `get_add_command_for_items`, then installed with the registry's shadcn CLI command:

- `@shadcn/card`, `@shadcn/badge`, `@shadcn/tabs`, `@shadcn/accordion`: https://ui.shadcn.com/
- `@react-bits/SpotlightCard-TS-CSS`: https://reactbits.dev/components/spotlight-card
- Existing `@shadcn/button` is reused for tool actions.

`FarmToolkit` enhances the home and farmer dashboard's eight tool links with shadcn cards, badges and buttons inside React Bits spotlight cards. Translated text and destination URLs come from the server-rendered fallback. The first card uses a dark forest surface. Other cards remain warm white; hover effects respect reduced motion.

`PestGuide` enhances saved disease entries with keyboard-accessible shadcn tabs for symptoms, treatment and prevention, with expandable treatment sections. Existing hash links, including the Treat now action and direct chemical-control links, select the matching tab and section. All six sections remain rendered by Django when JavaScript is unavailable. No HTML from authored content is injected into React.

The content editor keeps its Django form, upload validation, CSRF protection, crop-specific persistence and reset-after-save redirect. CSS provides paired desktop fields, a single mobile column and a sticky save action. Crop photograph selection is unchanged.

Run `npm run build` from `frontend/` to regenerate `static/frontend/`. Keep the emitted lazy CSS and JS chunks alongside the entry files. Only pages with matching islands load those components. No paid component subscription is required.

## Editorial home experience

`AgroLanding.tsx` and its scoped stylesheet add a photo-led home page with forest/lime surfaces, Plus Jakarta Sans and Instrument Serif typography, Motion reveals/parallax, filterable solution cards, crop library links, FAQs, and a getting-started CTA. The existing Krishi Mitra identity and account navigation remain in use. `templates/home.html` passes resolved existing URLs through data attributes; no backend changes are required. `home_fallback.html` preserves the previous translated content if JavaScript is unavailable.

The locally stored hero photograph is the Unsplash URL supplied in the design brief (`photo-1500382017468-9049fed747ef`), resized to 1920px; other images reuse the crop library assets and their existing credits. Pinterest could not be accessed, so no Pinterest photos or videos were copied. Sample partner logos, ratings, funding, and yield claims from the brief are omitted because they were not verified.

The landing page uses its own motion, bypassing legacy GSAP/Locomotive/WebGL enhancements. It honors reduced motion, uses lazy images below the fold, and preserves native touch scrolling. Production build/type checking and Chrome checks at 320/390/768/1024/1440px passed, including filters, FAQs, mobile menu, image loading, reduced motion, and library URLs. Safari/WebKit and Firefox test browsers were unavailable locally, so cross-engine verification remains incomplete.

## Detailed farming landing pages

The homepage now links to three frontend-only experiences: `/?experience=grow` (Plan & Grow), `/?experience=care` (Plant Care), and `/?experience=season` (Season & Markets). Query URLs reuse the existing home route and support direct navigation and refresh without backend changes. `DetailedLanding.tsx` supplies a hero, principles, a three-stage keyboard-accessible walkthrough, existing tool links, contextual guidance, related journeys, and a final CTA. Content lives in `experience-content.ts`.

`useLandingAnimation.ts` loads GSAP/ScrollTrigger for section movement and reading progress, plus Locomotive Scroll v5 for desktop wheel smoothing. It keeps native touch scrolling and excludes chat, navigation overlays, and native scroll regions. Three.js is dynamically imported for the decorative field study on capable desktops; the field uses instanced crops, a wireframe terrain, pointer rotation, and animated rings. It is illustrative, not a live field dashboard. The animation caps at 30fps, pauses when hidden/offscreen, and disposes GPU resources on cleanup. A static field illustration remains on small screens, reduced motion, Save-Data, or WebGL failure. Breakpoint/preference changes and page lifecycle events dispose and restore enhancements.

Validation: production TypeScript/Vite build passed. Chrome checked overview and all three query URLs at 320, 390, 768, 1024, and 1440px; all returned 200, with one H1, no horizontal overflow, and no JavaScript errors. Stage selection and keyboard Home navigation passed. Desktop WebGL canvas rendered. Reduced motion loaded no Three.js, ScrollTrigger, or Locomotive chunks. Safari/Firefox verification remains unavailable on this machine.

## Step-by-step tool guides

`ToolHowTo.tsx` adds an accessible “How to use” section at `#how-to-tools`, linked from the experience navigation. The overview includes all eight tools; each detailed landing includes its three relevant tools. `tool-guides.ts` contains five steps per tool, preparation requirements, a practical example, the expected result, and a link to the existing tool. Instructions were checked against the current templates and field definitions, including crop-advisor nutrient units, yield rainfall/area inputs, fertilizer planting modes, forecast activity explanations, mandi reporting dates, and crop-library navigation. No forms or backend behavior changed.

The tool selector supports keyboard arrows, Home, and End with linked tab/panel semantics. Desktop uses a sticky selector; smaller screens use a two-column selector and a single-column guide. Production build passed; Chrome verified all eight guides, five steps each, result links, keyboard wrapping, and no overflow at 320/390/768/1440px. All three detail pages display their relevant guides and default to their primary tool.

## Cultivation tips in the crop library

The library introduces a Cultivation Tips feature and labels all 70 crop cards. Every crop detail page includes `templates/crops/cultivation_tips.html` at `#cultivation-tips`: plant selection, site selection, field preparation, planting, monitoring, weeding, irrigation, organic fertilization, chemical fertilization, preventive measures, chemical plant protection, harvesting, and post-harvest. The repeated organic-fertilization request is represented once.

The guide uses the existing crop context for identity, planting material, climate, soil, irrigation notes, field practices, and companion/rotation guidance. Conditional explanations distinguish rice systems, aquatic lotus, grafted orchard plants, seed/seedling and vegetative propagation, grain/seed crops, flowers, underground produce, and fresh produce. General checklists are explicitly distinguished from sourced crop facts; missing crop-specific rates, spacing, dates, chemical choices, and storage targets are not fabricated. The page links existing crop sources and the reviewed APEDA, NC State, UMD, UC IPM, GAP, and FAO general references. Existing soil and climate data remain unchanged.

Native details provide 13 expandable topics without JavaScript. `static/js/cultivation.js` adds expand/collapse-all controls and opens topics on hash navigation. `static/css/cultivation.css` provides a desktop stage index and responsive mobile layout. No backend code, data models, or routes were changed. All 70 crop pages returned 200 and rendered 13 topics. Chrome checked rice/mango/lotus/potato/rose at 320/390/768/1440px, including no-overflow, controls, hash links, and native accordion operation with JavaScript disabled.

## Black shadcn IoT analytics dashboard

`/?experience=iot` opens a dedicated dashboard built with the existing shadcn/Base UI Card, Tabs, Badge, and Button components. Registry dashboard discovery and the shadcn tabs example informed the composition; no new dependencies were required. Homepage experience navigation and the authenticated farm dashboard link to the preview. Backend routes, APIs, and models remain unchanged.

`IoTDashboard.tsx` contains Overview, Analytics, and Devices views, four measurement cards, SVG trend charts with pointer and keyboard sample inspection, field/date filters, device health, field summaries, searchable/status-filtered inventory, mobile navigation, refresh feedback, and CSV export. `iot-demo-data.ts` isolates deterministic simulated readings and the example inventory. Exported files include a `demo_data` column and `demo` filename. The dashboard states that no hardware is connected; pairing, telemetry, calibration, and control are not implemented. Pest/disease alerts remain Coming soon. No credentials, integrations, or notification subscriptions were added.

The dashboard uses scoped black/neutral tokens and Bootstrap utility overrides, with a mobile dialog for navigation and native horizontal scrolling for the device table. It is lazy-loaded; landing-page Three.js, GSAP ScrollTrigger, and Locomotive bundles do not load for this view. Production TypeScript/Vite build passed. Chrome checked 320/390/768/1024/1440px without horizontal page overflow or JavaScript errors. Verified field/range changes, all analytics charts, keyboard sample inspection, shortening a selected sample range, search/status/no-results/reset, CSV downloads, refresh feedback, field-to-analytics navigation, and mobile drawer Escape behavior. Safari/Firefox remain unverified on this machine.
