import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Search, AlertCircle } from 'lucide-react';

interface UrlInputProps {
  onAnalyze: (url: string) => void;
  isLoading: boolean;
}

export const UrlInput = ({ onAnalyze, isLoading }: UrlInputProps) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const validateUrl = (url: string) => {
    const ebayPattern = /^https?:\/\/(www\.)?ebay\.(com|co\.uk|de|fr|it|es|ca|au)/i;
    return ebayPattern.test(url);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!url.trim()) {
      setError('Please enter an eBay product URL');
      return;
    }
    
    if (!validateUrl(url)) {
      setError('Please enter a valid eBay product URL');
      return;
    }
    
    onAnalyze(url);
  };

  return (
    <Card className="w-full max-w-2xl mx-auto p-8 shadow-lg border border-border/50">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground mb-2">
          Analyze eBay Seller
        </h2>
        <p className="text-muted-foreground">
          Paste any eBay product link to get instant seller analysis and trust insights
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <Input
            type="url"
            placeholder="https://www.ebay.com/itm/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="pr-12 h-12 text-base"
            disabled={isLoading}
          />
          <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
        </div>
        
        {error && (
          <div className="flex items-center gap-2 text-destructive text-sm">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}
        
        <Button 
          type="submit" 
          className="w-full h-12 bg-gradient-primary hover:opacity-90 transition-opacity"
          disabled={isLoading || !url.trim()}
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              Analyzing Seller...
            </div>
          ) : (
            'Analyze Seller'
          )}
        </Button>
      </form>
    </Card>
  );
};