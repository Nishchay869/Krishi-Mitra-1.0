import {
  Mail,
  Phone,
  MapPin,
  Sprout,
} from 'lucide-react';

export interface Footer4ColProps {
  className?: string;
}

// Brand Social Icon SVGs
function FacebookIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
    </svg>
  );
}

function InstagramIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
    </svg>
  );
}

function TwitterIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
    </svg>
  );
}

function GithubIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
    </svg>
  );
}

function DribbbleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm9.885 11.441c-2.574-.117-4.945.419-7.07 1.343-.328-.75-.688-1.503-1.077-2.247 2.656-1.123 4.887-2.738 6.44-4.832 1.109 1.644 1.707 3.593 1.707 5.736zm-3.08-7.391c-1.391 1.936-3.414 3.439-5.836 4.472-1.189-2.225-2.183-4.498-2.909-6.671 1.28-.431 2.651-.671 4.076-.671 1.75 0 3.398.423 4.669 1.17zm-9.014-1.139c.753 2.152 1.764 4.398 2.969 6.595-2.937 1.002-6.19 1.455-9.615 1.408.824-3.568 3.518-6.49 6.646-8.003zm-7.791 10.089c3.743.05 7.291-.452 10.485-1.57.362.709.7 1.434 1.009 2.155-3.324 1.954-5.69 4.962-6.845 8.784-2.821-1.802-4.649-4.877-4.649-8.369v-1zm9.645 10.669c1.075-3.642 3.308-6.486 6.467-8.312.87 2.378 1.31 4.954 1.188 7.551-2.151 1.347-4.708 2.053-7.406 2.053-.083 0-.166-.002-.249-.005v-.287zm9.034-2.483c.121-2.434-.301-4.856-1.134-7.094 1.921-.861 4.022-1.353 6.302-1.258-.231 3.253-1.898 6.13-4.453 8.352h-.715z"/>
    </svg>
  );
}

const data = {
  company: {
    name: 'Krishi Mitra',
    tagline: 'कृषि मित्र · AI Farming Companion',
    description:
      'AI-powered agricultural companion designed for Indian farmers. Diagnose plant diseases, track spraying conditions, monitor mandi rates, and make smarter farm decisions.',
    logo: '/static/images/logo-icon.png',
  },
  social: {
    facebook: 'https://facebook.com/krishimitra',
    instagram: 'https://instagram.com/krishimitra',
    twitter: 'https://twitter.com/krishimitra',
    github: 'https://github.com/krishimitra',
    dribbble: 'https://dribbble.com/krishimitra',
  },
  about: [
    { text: 'Project Mission', href: '/#about' },
    { text: 'Meet the Team', href: '/#team' },
    { text: 'Farmer Handbook', href: '/crops/tips/' },
    { text: 'Cultivation Guides', href: '/crops/library/' },
  ],
  services: [
    { text: 'Disease Diagnosis', href: '/disease/detect/' },
    { text: 'Spraying Advisory', href: '/weather/' },
    { text: 'Mandi Market Prices', href: '/market/' },
    { text: 'Crop Advisor & Yield', href: '/crops/recommend/' },
  ],
  helpful: [
    { text: 'Kisan Call Centre', href: 'tel:18001801551' },
    { text: 'Fertilizer Calculator', href: '/crops/fertilizer/' },
    { text: 'Live AI Assistant', href: '/chat/', hasIndicator: true },
    { text: 'My Farm Profile', href: '/accounts/profile/' },
  ],
  contact: {
    email: 'hello@krishimitra.in',
    phone: '1800-180-1551',
    address: 'Kolkata, West Bengal, India',
  },
};

export default function Footer4Col({ className = '' }: Footer4ColProps) {
  const socialLinks = [
    { icon: FacebookIcon, label: 'Facebook', href: data.social.facebook },
    { icon: InstagramIcon, label: 'Instagram', href: data.social.instagram },
    { icon: TwitterIcon, label: 'Twitter', href: data.social.twitter },
    { icon: GithubIcon, label: 'GitHub', href: data.social.github },
    { icon: DribbbleIcon, label: 'Dribbble', href: data.social.dribbble },
  ];

  return (
    <footer
      className={`app-footer-4col mt-16 w-full rounded-t-3xl bg-slate-900 text-slate-100 shadow-xl ${className}`}
      style={{
        borderTopLeftRadius: '28px',
        borderTopRightRadius: '28px',
      }}
    >
      <div className="mx-auto max-w-7xl px-4 pt-14 pb-28 sm:px-6 md:pb-24 lg:px-8 lg:pt-16">
        <div className="grid grid-cols-1 gap-10 lg:grid-cols-3">
          
          {/* Brand & Social Column */}
          <div className="text-center sm:text-left">
            <div className="flex items-center justify-center gap-3 sm:justify-start">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/40">
                <Sprout className="h-6 w-6" />
              </div>
              <span className="text-2xl font-bold tracking-tight text-white">
                {data.company.name}
              </span>
            </div>

            <p className="mt-4 max-w-md text-sm leading-relaxed text-slate-400 sm:max-w-sm sm:text-left mx-auto sm:mx-0">
              {data.company.description}
            </p>

            <ul className="mt-6 flex justify-center gap-4 sm:justify-start">
              {socialLinks.map(({ icon: Icon, label, href }) => (
                <li key={label}>
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-800 text-slate-300 transition-all hover:bg-emerald-500/20 hover:text-emerald-400 hover:scale-105"
                    aria-label={label}
                  >
                    <Icon className="h-5 w-5" />
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* 4 Navigation Columns (Responsive 2x2 on Mobile/Tabs, 4 cols on Desktop) */}
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-2 md:grid-cols-4 lg:col-span-2">
            
            {/* About Us */}
            <div>
              <p className="text-sm font-semibold tracking-wide text-white uppercase">About Us</p>
              <ul className="mt-4 space-y-3 text-sm">
                {data.about.map(({ text, href }) => (
                  <li key={text}>
                    <a
                      className="text-slate-400 transition hover:text-emerald-400"
                      href={href}
                    >
                      {text}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Our Services */}
            <div>
              <p className="text-sm font-semibold tracking-wide text-white uppercase">Our Services</p>
              <ul className="mt-4 space-y-3 text-sm">
                {data.services.map(({ text, href }) => (
                  <li key={text}>
                    <a
                      className="text-slate-400 transition hover:text-emerald-400"
                      href={href}
                    >
                      {text}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Helpful Links */}
            <div>
              <p className="text-sm font-semibold tracking-wide text-white uppercase">Helpful Links</p>
              <ul className="mt-4 space-y-3 text-sm">
                {data.helpful.map(({ text, href, hasIndicator }) => (
                  <li key={text}>
                    <a
                      href={href}
                      className="group inline-flex items-center gap-2 text-slate-400 transition hover:text-emerald-400"
                    >
                      <span>{text}</span>
                      {hasIndicator && (
                        <span className="relative flex h-2.5 w-2.5">
                          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                          <span className="relative inline-flex h-2.5 w-2.5 rounded-full bg-emerald-500" />
                        </span>
                      )}
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Contact Us */}
            <div>
              <p className="text-sm font-semibold tracking-wide text-white uppercase">Contact Us</p>
              <ul className="mt-4 space-y-3 text-sm">
                <li>
                  <a
                    className="flex items-center gap-2 text-slate-400 transition hover:text-emerald-400"
                    href={`mailto:${data.contact.email}`}
                  >
                    <Mail className="h-4 w-4 shrink-0 text-emerald-400" />
                    <span className="truncate">{data.contact.email}</span>
                  </a>
                </li>
                <li>
                  <a
                    className="flex items-center gap-2 text-slate-400 transition hover:text-emerald-400"
                    href={`tel:${data.contact.phone.replace(/[^0-9]/g, '')}`}
                  >
                    <Phone className="h-4 w-4 shrink-0 text-emerald-400" />
                    <span>{data.contact.phone}</span>
                  </a>
                </li>
                <li>
                  <div className="flex items-start gap-2 text-slate-400">
                    <MapPin className="h-4 w-4 shrink-0 text-emerald-400 mt-0.5" />
                    <address className="not-italic text-xs leading-relaxed text-slate-400">
                      {data.contact.address}
                    </address>
                  </div>
                </li>
              </ul>
            </div>

          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 border-t border-slate-800 pt-6">
          <div className="flex flex-col items-center justify-between gap-4 text-center sm:flex-row sm:text-left">
            <p className="text-xs text-slate-400">
              &copy; 2025 {data.company.name}. All rights reserved.
            </p>
            <p className="text-xs text-slate-500">
              Better decisions. Healthier farms. Advice grounded in Indian public agricultural sources.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
