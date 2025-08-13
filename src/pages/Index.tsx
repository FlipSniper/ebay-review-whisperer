import { useState } from 'react';
import { UrlInput } from '@/components/UrlInput';
import { SellerAnalysis } from '@/components/SellerAnalysis';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import heroImage from '@/assets/hero-image.jpg';

// Mock data for demonstration
const mockSellerData = {
  name: "TechDeals_Pro",
  location: "California, United States",
  feedbackScore: 45892,
  positivePercentage: 98.7,
  totalFeedback: 46534,
  memberSince: "2018",
  trustScore: 87,
  trustTrend: 'up' as const,
  sentimentSummary: {
    positive: 78,
    neutral: 15,
    negative: 7
  },
  commonIssues: ["Slow shipping", "Item condition", "Communication delays"],
  recentHighlights: {
    positive: [
      "Fast shipping, exactly as described. Great seller!",
      "Perfect condition, well packaged, highly recommend.",
      "Excellent communication and quick resolution of my question."
    ],
    negative: [
      "Item took longer to ship than expected",
      "Minor scratch not mentioned in description",
      "Seller slow to respond to messages"
    ]
  },
  shippingScore: 8.5,
  communicationScore: 7.8,
  itemDescriptionScore: 9.2
};

const Index = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [analyzedUrl, setAnalyzedUrl] = useState('');

  const handleAnalyze = async (url: string) => {
    setIsAnalyzing(true);
    setAnalyzedUrl(url);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setIsAnalyzing(false);
    setShowResults(true);
  };

  const handleBack = () => {
    setShowResults(false);
    setAnalyzedUrl('');
  };

  if (showResults) {
    return (
      <div className="min-h-screen bg-background py-8 px-4">
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleBack}
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Analyze Another Seller
          </Button>
        </div>
        <SellerAnalysis 
          sellerData={mockSellerData} 
          productUrl={analyzedUrl}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-primary/5 to-accent/5">
        <div className="container mx-auto px-4 py-16 lg:py-24">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="space-y-4">
                <h1 className="text-4xl lg:text-6xl font-bold text-foreground leading-tight">
                  Smart eBay
                  <span className="text-primary block">Seller Analysis</span>
                </h1>
                <p className="text-xl text-muted-foreground max-w-lg">
                  Get AI-powered insights on any eBay seller. Paste a product link and discover trust scores, sentiment analysis, and buyer feedback patterns.
                </p>
              </div>
              
              <div className="flex flex-wrap gap-4 text-sm">
                <div className="flex items-center gap-2 bg-trust-excellent/10 text-trust-excellent px-3 py-1 rounded-full">
                  <div className="w-2 h-2 bg-trust-excellent rounded-full"></div>
                  Trust Score Analysis
                </div>
                <div className="flex items-center gap-2 bg-primary/10 text-primary px-3 py-1 rounded-full">
                  <div className="w-2 h-2 bg-primary rounded-full"></div>
                  Sentiment Analysis
                </div>
                <div className="flex items-center gap-2 bg-warning/10 text-warning px-3 py-1 rounded-full">
                  <div className="w-2 h-2 bg-warning rounded-full"></div>
                  Risk Detection
                </div>
              </div>
            </div>
            
            <div className="relative">
              <img 
                src={heroImage}
                alt="eBay Seller Analysis Dashboard"
                className="rounded-xl shadow-2xl border border-border/50"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Form */}
      <div className="container mx-auto px-4 py-16">
        <UrlInput onAnalyze={handleAnalyze} isLoading={isAnalyzing} />
      </div>

      {/* Features */}
      <div className="bg-muted/30 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center text-foreground mb-12">
            How It Works
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center mx-auto">
                <span className="text-2xl font-bold text-primary">1</span>
              </div>
              <h3 className="text-xl font-semibold text-foreground">Paste URL</h3>
              <p className="text-muted-foreground">
                Simply paste any eBay product link into our analyzer
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-accent/10 rounded-xl flex items-center justify-center mx-auto">
                <span className="text-2xl font-bold text-accent">2</span>
              </div>
              <h3 className="text-xl font-semibold text-foreground">AI Analysis</h3>
              <p className="text-muted-foreground">
                Our AI analyzes seller data, reviews, and feedback patterns
              </p>
            </div>
            
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-trust-excellent/10 rounded-xl flex items-center justify-center mx-auto">
                <span className="text-2xl font-bold text-trust-excellent">3</span>
              </div>
              <h3 className="text-xl font-semibold text-foreground">Get Insights</h3>
              <p className="text-muted-foreground">
                Receive comprehensive trust scores and buying recommendations
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;