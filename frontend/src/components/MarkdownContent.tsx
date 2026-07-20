import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import '../components/landing/landing.css'

type MarkdownContentProps = {
  content: string
  className?: string
}

export function MarkdownContent({ content, className = 'landing-markdown' }: MarkdownContentProps) {
  return (
    <div className={className}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  )
}
