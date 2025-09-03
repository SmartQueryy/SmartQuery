import { Button } from "./ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"

export default function UITest() {
  return (
    <div className="p-4 space-y-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>shadcn/ui Test</CardTitle>
          <CardDescription>Testing shadcn/ui components</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <Button>Primary Button</Button>
            <Button variant="outline">Outline Button</Button>
          </div>
          <div className="flex gap-2">
            <Badge>Ready</Badge>
            <Badge variant="secondary">Processing</Badge>
            <Badge variant="destructive">Error</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}