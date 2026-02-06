
export interface StatCardProps {
  label: string;
  value: string | number;
  subValueText?: string;
  subValueColor?: string;
  icon: string;
  progress?: number;
}

export interface Appliance {
  id: string;
  name: string;
  brand: string;
  category: string;
  maxPower: number;
  mean12h: number;
  status: 'optimized' | 'high-load' | 'syncing' | 'idle';
  capabilities: string[];
}
