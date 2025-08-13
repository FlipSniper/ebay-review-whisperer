import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { TrustScore } from './TrustScore';
import { 
  User, 
  MapPin, 
  Star, 
  MessageSquare, 
  AlertTriangle, 
  ThumbsUp,
  Clock,
  Package
} from 'lucide-react';

interface SellerData {
  name: string;
  location: string;
  feedbackScore: number;
  positivePercentage: number;
  totalFeedback: number;
  memberSince: string;
  trustScore: number;
  trustTrend: 'up' | 'down' | 'stable';
  sentimentSummary: {
    positive: number;
    neutral: number;
    negative: number;
  };
  commonIssues: string[];
  recentHighlights: {
    positive: string[];
    negative: string[];
  };
  shippingScore: number;
  communicationScore: number;
  itemDescriptionScore: number;
}

interface SellerAnalysisProps {
  sellerData: SellerData;
  productUrl: string;
}

export const SellerAnalysis = ({ sellerData, productUrl }: SellerAnalysisProps) => {
  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">
          Seller Analysis Results
        </h1>
        <p className="text-muted-foreground">
          AI-powered analysis for better buying decisions
        </p>
      </div>

      {/* Trust Score and Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <TrustScore 
            score={sellerData.trustScore} 
            trend={sellerData.trustTrend}
            subtitle="Based on 500+ data points"
          />
        </div>
        
        <div className="lg:col-span-2">
          <Card className="p-6 h-full">
            <div className="flex items-center gap-2 mb-4">
              <User className="h-5 w-5 text-primary" />
              <h3 className="text-lg font-semibold">Seller Overview</h3>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-foreground">{sellerData.name}</h4>
                <div className="flex items-center gap-2 text-muted-foreground mt-1">
                  <MapPin className="h-4 w-4" />
                  <span>{sellerData.location}</span>
                  <Clock className="h-4 w-4 ml-2" />
                  <span>Member since {sellerData.memberSince}</span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Star className="h-4 w-4 text-warning fill-current" />
                    <span className="font-medium">{sellerData.feedbackScore.toLocaleString()}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">Feedback Score</p>
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <ThumbsUp className="h-4 w-4 text-trust-excellent" />
                    <span className="font-medium">{sellerData.positivePercentage}%</span>
                  </div>
                  <p className="text-xs text-muted-foreground">Positive Feedback</p>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>

      {/* Detailed Scores */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-3">
            <Package className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Shipping</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Score</span>
              <span className="font-medium">{sellerData.shippingScore}/10</span>
            </div>
            <Progress value={sellerData.shippingScore * 10} className="h-2" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-2 mb-3">
            <MessageSquare className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Communication</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Score</span>
              <span className="font-medium">{sellerData.communicationScore}/10</span>
            </div>
            <Progress value={sellerData.communicationScore * 10} className="h-2" />
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-2 mb-3">
            <Star className="h-5 w-5 text-primary" />
            <h3 className="font-semibold">Item Description</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Score</span>
              <span className="font-medium">{sellerData.itemDescriptionScore}/10</span>
            </div>
            <Progress value={sellerData.itemDescriptionScore * 10} className="h-2" />
          </div>
        </Card>
      </div>

      {/* Sentiment Analysis and Issues */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Sentiment Analysis</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-trust-excellent">Positive</span>
                <span>{sellerData.sentimentSummary.positive}%</span>
              </div>
              <Progress value={sellerData.sentimentSummary.positive} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-muted-foreground">Neutral</span>
                <span>{sellerData.sentimentSummary.neutral}%</span>
              </div>
              <Progress value={sellerData.sentimentSummary.neutral} className="h-2" />
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-trust-poor">Negative</span>
                <span>{sellerData.sentimentSummary.negative}%</span>
              </div>
              <Progress value={sellerData.sentimentSummary.negative} className="h-2" />
            </div>
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-warning" />
            <h3 className="text-lg font-semibold">Common Issues</h3>
          </div>
          <div className="space-y-2">
            {sellerData.commonIssues.map((issue, index) => (
              <Badge key={index} variant="outline" className="mr-2 mb-2">
                {issue}
              </Badge>
            ))}
          </div>
        </Card>
      </div>

      {/* Recent Highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-trust-excellent mb-4">
            Recent Positive Reviews
          </h3>
          <div className="space-y-3">
            {sellerData.recentHighlights.positive.map((highlight, index) => (
              <div key={index} className="text-sm text-muted-foreground italic border-l-2 border-trust-excellent pl-3">
                "{highlight}"
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h3 className="text-lg font-semibold text-trust-poor mb-4">
            Areas for Concern
          </h3>
          <div className="space-y-3">
            {sellerData.recentHighlights.negative.map((highlight, index) => (
              <div key={index} className="text-sm text-muted-foreground italic border-l-2 border-trust-poor pl-3">
                "{highlight}"
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};