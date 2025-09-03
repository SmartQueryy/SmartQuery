import { Card, CardContent } from '@/components/ui/card'
import { AlertCircle } from 'lucide-react'

interface ErrorDisplayProps {
  error: string
}

export function ErrorDisplay({ error }: ErrorDisplayProps) {
  return (
    <Card className="w-full border-destructive/50 bg-destructive/10">
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5">
            <AlertCircle className="h-4 w-4 text-destructive" />
          </div>
          <div>
            <h3 className="text-sm font-medium text-destructive mb-1">Authentication Error</h3>
            <p className="text-sm text-destructive/80">{error}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}