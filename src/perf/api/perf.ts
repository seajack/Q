import { http } from './http';

export type PerfRow = {
  id: number;
  name: string;
  role: string;
  dept: string;
  target: number; // 0-100
  grade: 'A+'|'A'|'A-'|'B+'|'B'|'B-'|'C';
  status: '进行中'|'已完成'|'待自评';
};

export type PerfListResp = {
  total: number;
  page: number;
  size: number;
  items: PerfRow[];
};

export async function fetchPerfList(params: {
  period: string;
  dept?: string;
  status?: string;
  minGrade?: string;
  maxGrade?: string;
  keyword?: string;
  page?: number;
  size?: number;
  sort?: string; // name|dept|target|grade, prefix '-' for desc
}) {
  const res = await http.get<PerfListResp>('/api/perf/list', { params });
  return res.data;
}

export async function fetchPerfDistribution(params: { period: string }) {
  const res = await http.get<{ bins: string[]; counts: number[] }>('/api/perf/distribution', { params });
  return res.data;
}

export async function fetchDeptProgress(params: { period: string }) {
  const res = await http.get<{ labels: string[]; values: number[] }>('/api/perf/dept-progress', { params });
  return res.data;
}

export async function fetchKpi(params: { period: string }) {
  const res = await http.get<{ doneRate: number; avgScore: number; avgGrade: string; pending: number; anomaly: number; anomalyRate: number }>('/api/perf/kpi', { params });
  return res.data;
}
