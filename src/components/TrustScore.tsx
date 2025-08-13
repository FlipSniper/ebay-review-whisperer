import { Card } from '@/components/ui/card';
import { Shield, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface TrustScoreProps {
  score: number;
  trend: 'up' | 'down' | 'stable';
  subtitle?: string;
}

export const TrustScore = ({ score, trend, subtitle }: TrustScoreProps) => {
  const getScoreLevel = (score: number) => {
    if (score >= 85) return { level: 'excellent', bg: 'bg-gradient-trust-excellent', text: 'text-trust-excellent' };
    if (score >= 70) return { level: 'good', bg: 'bg-gradient-trust-good', text: 'text-trust-good' };
    if (score >= 50) return { level: 'fair', bg: 'bg-gradient-trust-fair', text: 'text-trust-fair' };
    return { level: 'poor', bg: 'bg-gradient-trust-poor', text: 'text-trust-poor' };
  };

  const { level, bg, text } = getScoreLevel(score);
  
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-trust-excellent" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-trust-poor" />;
      default:
        return <Minus className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <Card className="p-6 text-center">
      <div className="flex items-center justify-center gap-2 mb-4">
        <Shield className="h-6 w-6 text-primary" />
        <h3 className="text-lg font-semibold">Trust Score</h3>
        {getTrendIcon()}
      </div>
      
      <div className={`relative w-32 h-32 mx-auto mb-4 rounded-full ${bg} p-1`}>
        <div className="w-full h-full bg-card rounded-full flex items-center justify-center">
          <div className="text-center">
            <div className={`text-3xl font-bold ${text}`}>
              {score}
            </div>
            <div className="text-xs text-muted-foreground uppercase tracking-wide">
              {level}
            </div>
          </div>
        </div>
      </div>
      
      {subtitle && (
        <p className="text-sm text-muted-foreground">
          {subtitle}
        </p>
      )}
    </Card>
  );
};