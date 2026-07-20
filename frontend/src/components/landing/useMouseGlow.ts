import { useEffect } from 'react'

export function useMouseGlow() {
  useEffect(() => {
    const mouseGlow = document.getElementById('mouse-glow')
    const mouseDot = document.getElementById('mouse-dot')
    if (!mouseGlow || !mouseDot) return

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReducedMotion) return

    let mouseX = window.innerWidth / 2
    let mouseY = window.innerHeight / 2
    let glowX = mouseX
    let glowY = mouseY
    let dotX = mouseX
    let dotY = mouseY
    let frame = 0

    const onMove = (event: MouseEvent) => {
      mouseX = event.clientX
      mouseY = event.clientY
    }

    const animate = () => {
      glowX += (mouseX - glowX) * 0.08
      glowY += (mouseY - glowY) * 0.08
      dotX += (mouseX - dotX) * 0.28
      dotY += (mouseY - dotY) * 0.28
      mouseGlow.style.transform = `translate(${glowX}px, ${glowY}px) translate(-50%, -50%)`
      mouseDot.style.transform = `translate(${dotX}px, ${dotY}px) translate(-50%, -50%)`
      frame = requestAnimationFrame(animate)
    }

    window.addEventListener('mousemove', onMove)
    frame = requestAnimationFrame(animate)

    return () => {
      window.removeEventListener('mousemove', onMove)
      cancelAnimationFrame(frame)
    }
  }, [])
}
