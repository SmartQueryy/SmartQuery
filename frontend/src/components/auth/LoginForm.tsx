import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { GoogleLoginButton } from './LoginButton'

export function LoginForm({
  className,
  onDevLogin,
  ...props
}: React.ComponentProps<"div"> & {
  onDevLogin?: () => void
}) {
  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader className="text-center">
          <CardTitle>Welcome back</CardTitle>
          <CardDescription>
            Sign in to access your data analysis dashboard
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-4">
            <GoogleLoginButton 
              size="lg" 
              redirectTo="/dashboard" 
              className="w-full" 
              showIcon={true} 
            />
            
            {onDevLogin && (
              <>
                <div className="relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t after:border-border">
                  <span className="relative z-10 bg-card px-2 text-muted-foreground">
                    For development
                  </span>
                </div>
                
                <Button 
                  onClick={onDevLogin}
                  variant="secondary"
                  className="w-full"
                  type="button"
                >
                  Dev Login (Bypass)
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}