import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import type { NavMenuItem, SiteBrand } from '../../api/types'

type LandingLinkProps = {
  href: string
  external?: boolean
  className?: string
  children: ReactNode
}

export function LandingLink({ href, external, className, children }: LandingLinkProps) {
  const isExternal = external || href.startsWith('http') || href.startsWith('mailto:')
  if (isExternal) {
    return (
      <a href={href} className={className} target="_blank" rel="noreferrer">
        {children}
      </a>
    )
  }
  if (href.startsWith('#')) {
    return (
      <a href={href} className={className}>
        {children}
      </a>
    )
  }
  return (
    <Link to={href} className={className}>
      {children}
    </Link>
  )
}

export function BrandLogo({ brand }: { brand: SiteBrand }) {
  if (brand.logo_url) {
    return <img src={brand.logo_url} alt={brand.brand_name} className="h-12 w-auto max-md:h-10" />
  }
  return null
}

export function renderMenu(items: NavMenuItem[] | undefined) {
  return (items ?? []).map((item) => (
    <li key={item.id}>
      <LandingLink
        href={item.href}
        external={item.is_external}
        className="text-[15px] font-medium text-white/60 transition hover:text-white"
      >
        {item.label}
      </LandingLink>
    </li>
  ))
}

export function renderFooterMenu(items: NavMenuItem[] | undefined) {
  return (items ?? []).map((item) => (
    <li key={item.id}>
      <LandingLink
        href={item.href}
        external={item.is_external}
        className="text-base font-medium text-white/50 transition hover:text-[var(--brand-primary)]"
      >
        {item.label}
      </LandingLink>
    </li>
  ))
}

export function CheckMark({ value }: { value: boolean }) {
  if (value) {
    return <span className="text-2xl font-bold landing-brand-text">✓</span>
  }
  return <span className="text-xl text-white/25">—</span>
}

export function WeakCheckMark({ value }: { value: boolean }) {
  if (value) {
    return <span className="text-2xl text-white/45">✓</span>
  }
  return <span className="text-xl text-white/25">—</span>
}
