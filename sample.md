'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { useState, useEffect, useRef } from 'react'
import {
FileText,
Zap,
Target,
Sparkles,
ArrowRight,
CheckCircle2,
Star,
Brain,
MessageCircle,
BarChart3,
Bot,
Download,
Github,
Mail,
Globe,
Briefcase,
Wand2,
Crown,
Check,
Quote,
X,
Clock,
Loader2
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useToast } from '@/components/ui/use-toast'

const features = [
{
icon: Target,
title: 'ATS-Optimized Resumes',
description: 'AI analyzes job descriptions and optimizes your resume to pass Applicant Tracking Systems with keyword matching and formatting.',
},
{
icon: Zap,
title: '5-Tier Optimization System',
description: 'Choose your optimization level from Quick Apply (30 sec) to Dream Job (20 min) based on how important each role is to you.',
},
{
icon: Brain,
title: 'AI Job Analysis',
description: 'Automatically extracts key requirements, skills, and qualifications from any job description to optimize your resume accordingly.',
},
{
icon: MessageCircle,
title: 'Interactive Resume Chatbot',
description: 'Edit and refine your resume in real-time using natural language. Ask AI to improve sections, add metrics, or fix formatting.',
},
{
icon: Bot,
title: 'Auto Apply (Beta)',
description: 'Paste a job application URL and let AI automatically fill out application forms for you, saving hours per application.',
},
{
icon: BarChart3,
title: 'Match Score Tracking',
description: 'See how well your resume matches each job with percentage scores. Track which applications perform best over time.',
},
{
icon: Briefcase,
title: 'Application History',
description: 'Track all your job applications, their status (applied, interview, offer), and manage your entire job search pipeline.',
},
{
icon: Wand2,
title: 'Smart Profile Builder',
description: 'Comprehensive profile management for experiences, projects, education, and skills with completion tracking and suggestions.',
},
{
icon: Download,
title: 'LaTeX & PDF Export',
description: 'Download professional LaTeX files or compile directly to PDF. Perfect formatting for any application system.',
},
]

const testimonials = [
{
name: 'Ashmit Sethi',
role: 'Software Engineer @ Meta',
avatar: 'AS',
content: 'Was mass applying to jobs and getting ghosted. Used ResumeAI for 2 weeks, got 4 interviews and landed an offer at Meta. The match scoring helped me prioritize which roles were actually worth my time.',
rating: 5,
},
{
name: 'Ashmit S.',
role: 'Product Manager @ Stripe',
avatar: 'AS',
content: 'The auto-apply feature is insane. What used to take me 45 mins per application now takes under 5. I applied to 30 companies in one weekend and heard back from 8.',
rating: 5,
},
{
name: 'Ashmit Sethi',
role: 'Data Scientist @ Airbnb',
avatar: 'AS',
content: 'Finally something that actually understands what recruiters look for. My resume went from a 45% match to 89% for my dream role. Got the interview, got the job.',
rating: 5,
},
{
name: 'Ashmit',
role: 'ML Engineer @ OpenAI',
avatar: 'AS',
content: 'I was skeptical about AI resume tools but this one actually works. The chatbot helped me rewrite my bullet points with actual metrics. Went from 0 callbacks to 6 in a month.',
rating: 5,
},
{
name: 'A. Sethi',
role: 'Founding Engineer @ YC Startup',
avatar: 'AS',
content: 'Used this while job hunting after my startup shut down. The tiered system is genius - I used Dream Job for the roles I really wanted and Quick Apply for the backup options. Landed exactly where I wanted.',
rating: 5,
},
]

const steps = [
{
number: '01',
title: 'Add Your Experience',
description: 'Upload your resume or manually enter your work history, projects, and skills.',
},
{
number: '02',
title: 'Paste Job Description',
description: 'Simply paste the job URL or description you want to apply for.',
},
{
number: '03',
title: 'Get Optimized Resume',
description: 'Our AI generates a perfectly tailored resume with match scoring.',
},
]

// Infinite scroll component for features (left to right)
function FeatureCarousel() {
const [isPaused, setIsPaused] = useState(false)
const scrollRef = useRef<HTMLDivElement>(null)

// Duplicate features for seamless loop
const duplicatedFeatures = [...features, ...features]

return (
<div className="relative overflow-hidden py-4">
{/_ Gradient masks _/}
<div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-gray-50 to-transparent z-10 pointer-events-none" />
<div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-gray-50 to-transparent z-10 pointer-events-none" />

      <div
        ref={scrollRef}
        className={cn(
          "flex gap-6",
          !isPaused && "animate-scroll-left"
        )}
        style={{
          width: 'max-content',
        }}
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => setIsPaused(false)}
      >
        {duplicatedFeatures.map((feature, index) => (
          <div
            key={`${feature.title}-${index}`}
            className="group relative flex-shrink-0 w-[320px] bg-white rounded-2xl p-6 shadow-sm border border-gray-100 transition-all duration-500 ease-out hover:shadow-lg hover:border-gray-300 hover:-translate-y-2 hover:scale-105"
          >
            <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-all duration-500 bg-gray-900 group-hover:scale-110 group-hover:rotate-2">
              <feature.icon className="h-6 w-6 text-white transition-transform duration-500" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2 transition-colors duration-300">
              {feature.title}
            </h3>
            <p className="text-sm text-gray-600 transition-all duration-500 line-clamp-2 group-hover:opacity-90">
              {feature.description}
            </p>
          </div>
        ))}
      </div>
    </div>

)
}

// Newsletter form component
function NewsletterForm() {
const [email, setEmail] = useState('')
const [isLoading, setIsLoading] = useState(false)
const { toast } = useToast()

const handleSubmit = async (e: React.FormEvent) => {
e.preventDefault()
if (!email || !email.includes('@')) {
toast({
title: 'Invalid email',
description: 'Please enter a valid email address',
variant: 'destructive',
})
return
}

    setIsLoading(true)
    try {
      const response = await fetch('/api/newsletter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to subscribe')
      }

      toast({
        title: 'Successfully subscribed!',
        description: 'You\'ll receive our latest updates and tips.',
      })
      setEmail('')
    } catch (error) {
      toast({
        title: 'Subscription failed',
        description: error instanceof Error ? error.message : 'Please try again later',
        variant: 'destructive',
      })
    } finally {
      setIsLoading(false)
    }

}

return (
<form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
<div className="relative flex-1 sm:w-80">
<Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
<Input
type="email"
placeholder="Enter your email"
value={email}
onChange={(e) => setEmail(e.target.value)}
disabled={isLoading}
className="pl-10 h-11 bg-white border-gray-300 focus:border-gray-900 focus:ring-gray-900"
required
/>
</div>
<Button
        type="submit"
        disabled={isLoading}
        className="h-11 px-6 bg-gray-900 hover:bg-gray-800 text-white"
      >
{isLoading ? (
<>
<Loader2 className="h-4 w-4 mr-2 animate-spin" />
Subscribing...
</>
) : (
<>
Join
<ArrowRight className="ml-2 h-4 w-4" />
</>
)}
</Button>
</form>
)
}

// Infinite scroll component for testimonials (right to left)
function TestimonialCarousel() {
const [isPaused, setIsPaused] = useState(false)
const [expandedTestimonial, setExpandedTestimonial] = useState<number | null>(null)

// Duplicate testimonials for seamless loop
const duplicatedTestimonials = [...testimonials, ...testimonials]

return (
<div className="relative overflow-hidden py-4">
{/_ Gradient masks _/}
<div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-white to-transparent z-10 pointer-events-none" />
<div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-white to-transparent z-10 pointer-events-none" />

      <div
        className={cn(
          "flex gap-6",
          !isPaused && "animate-scroll-right"
        )}
        style={{
          width: 'max-content',
        }}
        onMouseEnter={() => setIsPaused(true)}
        onMouseLeave={() => {
          setIsPaused(false)
          setExpandedTestimonial(null)
        }}
      >
        {duplicatedTestimonials.map((testimonial, index) => (
          <div
            key={`${testimonial.name}-${index}`}
            onClick={() => setExpandedTestimonial(expandedTestimonial === index ? null : index)}
            className={cn(
              "group relative flex-shrink-0 w-[380px] bg-gray-50 rounded-2xl p-6 border border-gray-100 cursor-pointer transition-all duration-300 ease-out",
              expandedTestimonial === index
                ? "scale-105 shadow-xl bg-white border-gray-300 z-20"
                : "hover:bg-white hover:shadow-md hover:border-gray-200 hover:-translate-y-1"
            )}
          >
            <div className="flex items-start gap-4 mb-4">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gray-900 to-gray-700 flex items-center justify-center text-white font-semibold text-sm">
                {testimonial.avatar}
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                <p className="text-sm text-gray-500">{testimonial.role}</p>
              </div>
              <Quote className="h-8 w-8 text-gray-200 group-hover:text-gray-300 transition-colors" />
            </div>
            <div className="flex gap-0.5 mb-3">
              {[...Array(testimonial.rating)].map((_, i) => (
                <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
              ))}
            </div>
            <p className={cn(
              "text-gray-600 text-sm leading-relaxed transition-all duration-300",
              expandedTestimonial === index ? "line-clamp-none" : "line-clamp-3"
            )}>
              &quot;{testimonial.content}&quot;
            </p>
          </div>
        ))}
      </div>

      {/* Expanded testimonial modal overlay */}
      {expandedTestimonial !== null && (
        <div
          className="fixed inset-0 bg-black/20 z-30 backdrop-blur-sm"
          onClick={() => setExpandedTestimonial(null)}
        />
      )}
    </div>

)
}

export default function LandingPage() {
return (
<div className="min-h-screen bg-white">
{/_ Navigation _/}
<nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b">
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
<div className="flex items-center justify-between h-16">
<Link href="/" className="flex items-center gap-2">
<FileText className="h-8 w-8" />
<span className="text-xl font-bold">ResumeAI</span>
</Link>
<div className="hidden lg:flex items-center gap-8">
<Link href="#how-it-works" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
Features
</Link>
<Link href="#pricing" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
Pricing
</Link>
<Link href="/dashboard" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
Dashboard
</Link>
<Link href="/terms" className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors">
Resources
</Link>
</div>
<div className="flex items-center gap-3">
<Button variant="ghost" size="sm" className="hidden sm:flex" asChild>
<Link href="/login">Sign In</Link>
</Button>
<Button size="sm" asChild>
<Link href="/signup">Get Started</Link>
</Button>
</div>
</div>
</div>
</nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto">
            <div className="inline-flex items-center gap-2 bg-gray-100 rounded-full px-4 py-1.5 text-sm font-medium mb-8">
              <Sparkles className="h-4 w-4" />
              <span>AI-Powered Resume Optimization</span>
            </div>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tight text-gray-900">
              Land more interviews with{' '}
              <span className="bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                AI-optimized
              </span>{' '}
              resumes
            </h1>
            <p className="mt-8 text-xl text-gray-600 max-w-2xl mx-auto">
              Stop sending generic resumes. ResumeAI tailors your resume for each job application with AI-powered optimization,
              match scoring, interactive editing, and automated application filling. Increase your chances of getting past ATS and landing interviews.
            </p>
            <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="lg" className="h-12 px-8 text-base" asChild>
                <Link href="/signup">
                  Start Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="h-12 px-8 text-base" asChild>
                <Link href="#how-it-works">See How It Works</Link>
              </Button>
            </div>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-4 text-sm text-gray-600">
              <div className="flex items-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span>Free to start</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span>AI-powered optimization</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span>LaTeX & PDF export</span>
              </div>
              <div className="flex items-center gap-1">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span>Application tracking</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section - Auto-scrolling carousel */}
      <section className="py-20 bg-gray-50 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Why choose ResumeAI?
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Our platform combines AI intelligence with industry expertise to create
              resumes that get results.
            </p>
          </div>
        </div>
        <FeatureCarousel />
      </section>

      {/* How it Works Section - Fixed */}
      <section id="how-it-works" className="py-20 bg-white">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              How it works
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Get a tailored resume in three simple steps
            </p>
          </div>
          <div className="relative">
            {/* Connection line */}
            <div className="hidden md:block absolute top-12 left-[16.67%] right-[16.67%] h-0.5 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200" />

            <div className="grid md:grid-cols-3 gap-12 md:gap-8">
              {steps.map((step, index) => (
                <div key={step.number} className="relative text-center">
                  {/* Step number circle */}
                  <div className="relative inline-flex items-center justify-center w-24 h-24 mb-6">
                    <div className="absolute inset-0 bg-gray-100 rounded-full" />
                    <span className="relative text-4xl font-bold text-gray-900">
                      {step.number}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 max-w-xs mx-auto">
                    {step.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section - Auto-scrolling carousel */}
      <section className="py-20 bg-white overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              People are landing jobs
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Join thousands of job seekers who&apos;ve used ResumeAI to get interviews at top companies.
            </p>
          </div>
        </div>
        <TestimonialCarousel />
      </section>

      {/* Pricing Section - More human copy */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Try it free. Upgrade if you love it.
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Most people stick with free. Power users go Pro. You&apos;ll know which one you are after your first resume.
            </p>
          </div>

          {/* Pricing Cards */}
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free Plan */}
            <div className="group bg-white rounded-2xl p-8 border border-gray-200 shadow-sm hover:shadow-xl hover:-translate-y-2 hover:border-gray-300 transition-all duration-500 ease-out cursor-pointer">
              <div className="h-12 w-12 bg-gray-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-gray-900 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500">
                <Zap className="h-6 w-6 text-gray-600 group-hover:text-white transition-colors duration-500" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 group-hover:text-gray-900 transition-colors duration-300">Free</h3>
              <p className="text-sm text-gray-600 mt-1 group-hover:text-gray-700 transition-colors duration-300">Perfect for getting started</p>
              <div className="mt-4 mb-6 group-hover:scale-105 transition-transform duration-500">
                <span className="text-4xl font-bold text-gray-900">$0</span>
                <span className="text-gray-500">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                {['3 tailored resumes/month', 'AI optimization', 'ATS-friendly formatting', 'Match scoring', 'PDF export'].map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-gray-700 group-hover:text-gray-900 transition-all duration-300" style={{ transitionDelay: `${i * 50}ms` }}>
                    <Check className="h-4 w-4 text-green-500 shrink-0 group-hover:scale-110 group-hover:rotate-12 transition-transform duration-300" />
                    <span className="group-hover:translate-x-1 transition-transform duration-300">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button variant="outline" className="w-full group-hover:bg-gray-900 group-hover:text-white group-hover:border-gray-900 transition-all duration-500" asChild>
                <Link href="/signup" className="flex items-center justify-center gap-2">
                  Get Started Free
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-300" />
                </Link>
              </Button>
            </div>

            {/* Pro Plan */}
            <div className="group bg-white rounded-2xl p-8 border-2 border-blue-500 shadow-lg relative hover:shadow-2xl hover:-translate-y-3 hover:scale-105 hover:border-blue-600 transition-all duration-500 ease-out cursor-pointer">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 group-hover:scale-110 group-hover:-rotate-3 transition-all duration-500">
                <Badge className="bg-blue-500 hover:bg-blue-500 text-white px-4 animate-pulse">
                  Most Popular
                </Badge>
              </div>
              <div className="h-12 w-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-gradient-to-br group-hover:from-blue-500 group-hover:to-blue-600 group-hover:scale-125 group-hover:rotate-6 transition-all duration-500">
                <Sparkles className="h-6 w-6 text-blue-600 group-hover:text-white group-hover:animate-pulse transition-colors duration-500" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">Pro</h3>
              <p className="text-sm text-gray-600 mt-1 group-hover:text-gray-700 transition-colors duration-300">For active job seekers</p>
              <div className="mt-4 mb-6 group-hover:scale-110 transition-transform duration-500">
                <span className="text-4xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors duration-300">$9</span>
                <span className="text-gray-500">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                {['30 tailored resumes/month', 'Everything in Free', 'Auto-Apply feature', 'Unlimited AI chat edits', 'Premium templates', 'Application tracking'].map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-gray-700 group-hover:text-gray-900 transition-all duration-300" style={{ transitionDelay: `${i * 50}ms` }}>
                    <Check className="h-4 w-4 text-green-500 shrink-0 group-hover:scale-110 group-hover:rotate-12 group-hover:text-blue-500 transition-all duration-300" />
                    <span className="group-hover:translate-x-1 transition-transform duration-300">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button className="w-full bg-blue-500 hover:bg-blue-600 group-hover:bg-gradient-to-r group-hover:from-blue-500 group-hover:to-blue-600 group-hover:shadow-lg group-hover:scale-105 transition-all duration-500" asChild>
                <Link href="/signup" className="flex items-center justify-center gap-2">
                  Start Pro Trial
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-2 transition-transform duration-300" />
                </Link>
              </Button>
            </div>

            {/* Unlimited Plan */}
            <div className="group bg-white rounded-2xl p-8 border border-gray-200 shadow-sm hover:shadow-xl hover:-translate-y-2 hover:border-purple-300 transition-all duration-500 ease-out cursor-pointer">
              <div className="h-12 w-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-gradient-to-br group-hover:from-purple-500 group-hover:to-purple-600 group-hover:scale-110 group-hover:-rotate-3 transition-all duration-500">
                <Crown className="h-6 w-6 text-purple-600 group-hover:text-white group-hover:animate-pulse transition-colors duration-500" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 group-hover:text-purple-600 transition-colors duration-300">Unlimited</h3>
              <p className="text-sm text-gray-600 mt-1 group-hover:text-gray-700 transition-colors duration-300">For power users</p>
              <div className="mt-4 mb-6 group-hover:scale-105 transition-transform duration-500">
                <span className="text-4xl font-bold text-gray-900 group-hover:text-purple-600 transition-colors duration-300">$19</span>
                <span className="text-gray-500">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                {['Unlimited resumes', 'Everything in Pro', 'Priority support', 'Advanced analytics', 'API access', 'Custom branding'].map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-gray-700 group-hover:text-gray-900 transition-all duration-300" style={{ transitionDelay: `${i * 50}ms` }}>
                    <Check className="h-4 w-4 text-green-500 shrink-0 group-hover:scale-110 group-hover:rotate-12 group-hover:text-purple-500 transition-all duration-300" />
                    <span className="group-hover:translate-x-1 transition-transform duration-300">{feature}</span>
                  </li>
                ))}
              </ul>
              <Button variant="secondary" className="w-full group-hover:bg-purple-600 group-hover:text-white group-hover:border-purple-600 group-hover:shadow-lg group-hover:scale-105 transition-all duration-500" asChild>
                <Link href="/signup" className="flex items-center justify-center gap-2">
                  Go Unlimited
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform duration-300" />
                </Link>
              </Button>
            </div>
          </div>

          <p className="text-center text-sm text-gray-500 mt-8">
            Save 20% with annual billing.{' '}
            <Link href="/pricing" className="text-blue-600 hover:underline">
              View full pricing details →
            </Link>
          </p>
        </div>
      </section>

      {/* AI-Powered Optimization Tiers Section */}
      <section className="py-20 bg-gradient-to-b from-white to-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Optimize your way
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-3xl mx-auto">
              Our advanced AI analyzes each role and generates personalized questions based on job requirements,
              skill gaps, and your experience. Choose your optimization level based on how important the role is to you.
            </p>
          </div>

          {/* How It Works */}
          <div className="mb-16 bg-white rounded-2xl p-8 border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-300">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-lg bg-gray-900 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900">How it works</h3>
            </div>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="group flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors duration-300">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center font-bold text-sm group-hover:bg-gray-900 group-hover:text-white transition-all duration-300">
                  1
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">AI analyzes the role</h4>
                  <p className="text-sm text-gray-600">
                    Our AI reads the job description, identifies key requirements, technical skills, and industry context.
                  </p>
                </div>
              </div>
              <div className="group flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors duration-300">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center font-bold text-sm group-hover:bg-gray-900 group-hover:text-white transition-all duration-300">
                  2
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">Personalized questions</h4>
                  <p className="text-sm text-gray-600">
                    Based on your profile and the role, AI generates targeted questions to uncover relevant experience and achievements.
                  </p>
                </div>
              </div>
              <div className="group flex items-start gap-4 p-4 rounded-xl hover:bg-gray-50 transition-colors duration-300">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-100 text-gray-700 flex items-center justify-center font-bold text-sm group-hover:bg-gray-900 group-hover:text-white transition-all duration-300">
                  3
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">Optimized resume</h4>
                  <p className="text-sm text-gray-600">
                    Your resume is tailored with perfect keyword matching, quantified achievements, and ATS optimization.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Optimization Tiers */}
          <div className="grid md:grid-cols-5 gap-4 mb-12">
            {[
              {
                tier: 1,
                name: 'Quick Apply',
                desc: 'Fully automated',
                questions: '0 questions',
                time: '30 seconds',
                optimization: 'Basic keyword matching',
                icon: Zap
              },
              {
                tier: 2,
                name: 'Standard',
                desc: 'Light optimization',
                questions: '2-3 questions',
                time: '2-3 minutes',
                optimization: 'Moderate keyword optimization',
                icon: Target
              },
              {
                tier: 3,
                name: 'Priority',
                desc: 'Balanced approach',
                questions: '3 questions',
                time: '5 minutes',
                optimization: 'Thorough optimization',
                icon: Star
              },
              {
                tier: 4,
                name: 'High Priority',
                desc: 'Deep optimization',
                questions: '5 questions',
                time: '8-10 minutes',
                optimization: 'Comprehensive rewrite',
                icon: Crown
              },
              {
                tier: 5,
                name: 'Dream Job',
                desc: 'Maximum effort',
                questions: '8 questions',
                time: '15-20 minutes',
                optimization: 'Perfect alignment',
                icon: Sparkles
              },
            ].map((item) => {
              const Icon = item.icon

              return (
                <div
                  key={item.tier}
                  className="group relative bg-white rounded-xl p-6 border-2 border-gray-200 text-center hover:border-gray-400 hover:shadow-xl hover:-translate-y-2 hover:scale-105 cursor-pointer transition-all duration-500 ease-out"
                >
                  {/* Tier Badge */}
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                    <div className="bg-gray-900 text-white text-xs font-bold px-3 py-1 rounded-full group-hover:scale-110 transition-transform duration-300">
                      Tier {item.tier}
                    </div>
                  </div>

                  {/* Icon - All use consistent gray/black scheme */}
                  <div className="mx-auto mb-4 h-12 w-12 rounded-xl flex items-center justify-center transition-all duration-500 bg-gray-100 text-gray-700 group-hover:bg-gray-900 group-hover:text-white group-hover:scale-110 group-hover:rotate-3">
                    <Icon className="h-6 w-6" />
                  </div>

                  {/* Name */}
                  <h3 className="font-bold text-lg text-gray-900 mb-1 group-hover:scale-105 transition-transform duration-300">
                    {item.name}
                  </h3>

                  {/* Description */}
                  <p className="text-xs text-gray-500 mb-4 group-hover:text-gray-700 transition-colors duration-300">
                    {item.desc}
                  </p>

                  {/* Stats */}
                  <div className="space-y-2 mb-4 text-left">
                    <div className="flex items-center gap-2 text-xs text-gray-600 group-hover:text-gray-900 transition-colors duration-300">
                      <MessageCircle className="h-3 w-3 text-gray-400 group-hover:text-gray-600 transition-colors duration-300" />
                      <span className="font-medium">{item.questions}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-600 group-hover:text-gray-900 transition-colors duration-300">
                      <Clock className="h-3 w-3 text-gray-400 group-hover:text-gray-600 transition-colors duration-300" />
                      <span>{item.time}</span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-600 group-hover:text-gray-900 transition-colors duration-300">
                      <Sparkles className="h-3 w-3 text-gray-400 group-hover:text-gray-600 transition-colors duration-300" />
                      <span className="line-clamp-2">{item.optimization}</span>
                    </div>
                  </div>

                  {/* Stars - Keep yellow for visual hierarchy */}
                  <div className="flex justify-center gap-1 mb-2 group-hover:scale-110 transition-transform duration-500">
                    {[...Array(item.tier)].map((_, i) => (
                      <Star
                        key={i}
                        className="h-3 w-3 fill-gray-300 text-gray-300 group-hover:fill-gray-900 group-hover:text-gray-900 group-hover:scale-125 group-hover:rotate-12 transition-all duration-300"
                        style={{ transitionDelay: `${i * 50}ms` }}
                      />
                    ))}
                  </div>
                </div>
              )
            })}
          </div>

          {/* AI Question Generation Info */}
          <div className="bg-gradient-to-br from-gray-50 to-white rounded-2xl p-8 border border-gray-200">
            <div className="flex items-center gap-3 mb-6">
              <div className="h-10 w-10 rounded-lg bg-gray-900 flex items-center justify-center">
                <Brain className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-gray-900">AI-generated questions</h3>
                <p className="text-sm text-gray-600">Questions adapt based on the role and your profile</p>
              </div>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600 max-w-2xl mx-auto">
                <strong className="text-gray-900">Smart matching:</strong> Our AI identifies skill gaps,
                matches transferable skills, and asks questions that maximize your match score.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="group bg-gray-900 rounded-3xl p-12 text-center hover:scale-[1.02] hover:shadow-2xl transition-all duration-500">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Ready to land your dream job?
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-8">
              Join thousands of job seekers who are using ResumeAI to optimize their
              applications and get more interviews.
            </p>
            <Button size="lg" variant="secondary" className="h-12 px-8 text-base group-hover:scale-105 transition-transform duration-300" asChild>
              <Link href="/signup">
                Get Started for Free
                <ArrowRight className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform duration-300" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Newsletter Section */}
          <div className="py-12 border-b border-gray-200">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Subscribe to our newsletter
                </h3>
                <p className="text-sm text-gray-600 max-w-md">
                  Get the latest on new ResumeAI features, job search tips, and creative ways to level up your applications every week.
                </p>
              </div>
              <NewsletterForm />
            </div>
          </div>

          {/* Main Footer Content */}
          <div className="py-12">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
              {/* Logo and Brand */}
              <div className="md:col-span-1">
                <Link href="/" className="flex items-center gap-2 mb-4">
                  <div className="h-10 w-10 bg-gray-900 rounded-lg flex items-center justify-center">
                    <FileText className="h-6 w-6 text-white" />
                  </div>
                  <span className="text-xl font-bold text-gray-900">ResumeAI</span>
                </Link>
                <p className="text-sm text-gray-600">
                  AI-powered resume optimization to help you land more interviews.
                </p>
              </div>

              {/* Quick Navigation */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-4">Quick Navigation</h4>
                <ul className="space-y-3">
                  <li>
                    <Link href="#how-it-works" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
                      How it works
                    </Link>
                  </li>
                  <li>
                    <Link href="#pricing" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
                      Pricing
                    </Link>
                  </li>
                  <li>
                    <Link href="/dashboard" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
                      Dashboard
                    </Link>
                  </li>
                </ul>
              </div>

              {/* Info */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-4">Info</h4>
                <ul className="space-y-3">
                  <li>
                    <Link href="/terms" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
                      Terms of use
                    </Link>
                  </li>
                  <li>
                    <Link href="/privacy" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">
                      Privacy
                    </Link>
                  </li>
                </ul>
              </div>

              {/* Social Links */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-4">Connect</h4>
                <div className="flex flex-col gap-3">
                  <a
                    href="https://www.github.com/1300Sarthak"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                    aria-label="GitHub"
                  >
                    <Github className="h-4 w-4" />
                    <span>GitHub</span>
                  </a>
                  <a
                    href="mailto:sarthakluv@gmail.com"
                    className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                    aria-label="Email"
                  >
                    <Mail className="h-4 w-4" />
                    <span>Email</span>
                  </a>
                  <a
                    href="https://sarthak.lol"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                    aria-label="Portfolio"
                  >
                    <Globe className="h-4 w-4" />
                    <span>Portfolio</span>
                  </a>
                </div>
              </div>
            </div>

            {/* Copyright */}
            <div className="pt-8 border-t border-gray-200">
              <p className="text-sm text-gray-500 text-center">
                ResumeAI. All rights reserved. © {new Date().getFullYear()}
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>

)
}
