import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CloudArrowUpIcon, ChatBubbleLeftRightIcon, MagnifyingGlassIcon, ChartBarIcon, ShieldCheckIcon, TableCellsIcon } from "@heroicons/react/24/outline"

const FEATURES = [
  { label: "Upload CSVs Instantly", icon: <CloudArrowUpIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "Ask Data Questions", icon: <ChatBubbleLeftRightIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "AI-Powered Insights", icon: <MagnifyingGlassIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "Visualize Results", icon: <ChartBarIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "Secure & Private", icon: <ShieldCheckIcon className="h-5 w-5 text-muted-foreground" /> },
  { label: "No SQL Needed", icon: <TableCellsIcon className="h-5 w-5 text-muted-foreground" /> },
]

export function FeaturesPreview() {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-base">What you can do with SmartQuery</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {FEATURES.map((feature) => (
            <div key={feature.label} className="flex items-center gap-3 text-sm text-muted-foreground">
              {feature.icon}
              <span>{feature.label}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}