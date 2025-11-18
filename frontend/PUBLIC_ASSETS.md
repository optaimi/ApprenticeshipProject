# Static Assets in Next.js

This guide explains where to place and how to use static files (images, logos, etc.) in the frontend.

## Directory Structure

```
frontend/
├── public/
│   ├── logo.svg              ← Logos go here
│   ├── favicon.ico           ← Browser tab icon
│   └── images/               ← Other images
│       ├── hero.png
│       └── icon-check.svg
├── app/
│   ├── page.tsx
│   └── layout.tsx
└── components/
```

## How to Add Files

### 1. Place files in `public/` folder

Example: `frontend/public/logo.svg`

### 2. Reference them in code

#### In React components:
```tsx
// Using img tag
<img src="/logo.svg" alt="Logo" />

// Using Next.js Image component (optimized)
import Image from 'next/image'

export default function Header() {
  return (
    <Image
      src="/logo.svg"
      alt="JH Logo"
      width={40}
      height={40}
    />
  )
}
```

#### In CSS:
```css
.header {
  background-image: url('/logo.svg');
}
```

## Current Assets

- **logo.svg** - JH branding logo (40x40, blue background with white text)

## File Types Supported

- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`
- Icons: `.svg`, `.ico`
- Fonts: `.woff`, `.woff2`, `.ttf`
- Documents: `.pdf`

## Replacing the Logo

To use your own logo:

1. Replace `frontend/public/logo.svg` with your logo file
2. Or add a new file: `frontend/public/my-logo.png`
3. Update the reference in `components/Logo.tsx`:

```tsx
// Current (component-based)
<div className="...">JH</div>

// Or use image file
<img src="/my-logo.png" alt="Logo" width={40} height={40} />
```

## Best Practices

✅ **Do:**
- Use SVG for logos (scalable, small file size)
- Compress images before uploading
- Use descriptive file names: `logo-jh.svg`, not `logo1.svg`
- Use the Next.js `Image` component for optimization

❌ **Don't:**
- Store large files in public (use CDN instead)
- Use spaces in filenames (use hyphens: `my-logo.svg`)
- Put sensitive files in public (they're publicly accessible!)

## File Size Guidelines

| File Type | Recommended Size |
|-----------|-----------------|
| Logo | < 50 KB |
| Icon | < 20 KB |
| Image | < 500 KB |
| Hero Image | < 1 MB |

## Using the Next.js Image Component

For optimized images, use the Image component:

```tsx
import Image from 'next/image'

<Image
  src="/hero.png"
  alt="Hero image"
  width={1200}
  height={600}
  priority  // Load immediately
/>
```

Benefits:
- Automatic optimization
- Responsive sizing
- Lazy loading
- WebP conversion

## Accessing Public Assets

Files in `public/` are served at the root path:

- `frontend/public/logo.svg` → `http://localhost:3000/logo.svg`
- `frontend/public/images/icon.svg` → `http://localhost:3000/images/icon.svg`

## Current Logo Component

The Logo component (`components/Logo.tsx`) currently renders text "JH" with styling:

```tsx
<div className="bg-blue-600 text-white font-bold rounded-lg">
  JH
</div>
```

You can:
1. Keep this text-based approach
2. Replace with an image: `<img src="/logo.svg" alt="JH" />`
3. Use Next.js Image: `<Image src="/logo.svg" alt="JH" width={40} height={40} />`

---

**Note**: Changes to files in `public/` don't require dev server restart. Just refresh the browser.
