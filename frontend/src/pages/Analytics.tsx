import { AnalyticsDashboard } from '../components/AnalyticsDashboard';
import { useLanguage } from '../contexts/LanguageContext';

export default function Analytics() {
  const { language } = useLanguage();
  
  return <AnalyticsDashboard language={language} />;
}

