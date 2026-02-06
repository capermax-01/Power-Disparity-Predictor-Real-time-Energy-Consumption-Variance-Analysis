
export interface Project {
  id: string;
  title: string;
  category: string;
  tag: string;
  image: string;
}

export interface Article {
  id: string;
  title: string;
  date: string;
  description: string;
  image: string;
}

export interface ExperienceEntry {
  id: string;
  title: string;
  company: string;
  period: string;
  location: string;
  current?: boolean;
  bulletPoints: string[];
}
